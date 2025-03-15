from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uvicorn

from src.blockchain.blockchain import MedicalBlockchain
from src.ai_analytics.health_analyzer import HealthAnalyzer
from src.data_management.medical_data import MedicalDataManager

# Security configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title="Decentralized Medical Data Management",
    description="AI-driven decentralized platform for medical data management",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
blockchain = MedicalBlockchain("http://localhost:8545")
health_analyzer = HealthAnalyzer()
data_manager = MedicalDataManager()


# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


class MedicalData(BaseModel):
    patient_data: Dict[str, Any]
    timestamp: datetime = datetime.now()


# Security functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data


# API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real application, validate against a database
    # This is a simplified example
    if form_data.username != "test" or form_data.password != "test":
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/medical-record/")
async def create_medical_record(
    medical_data: MedicalData, current_user: User = Depends(get_current_user)
):
    """Create a new medical record"""
    try:
        # Store in data manager
        record_id = data_manager.add_record(
            current_user.username, medical_data.patient_data
        )

        # Add to blockchain
        blockchain.add_transaction(
            sender=current_user.username,
            recipient=current_user.username,
            data={"record_id": record_id, "timestamp": str(medical_data.timestamp)},
        )

        return {"status": "success", "record_id": record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/medical-record/{record_id}")
async def get_medical_record(
    record_id: str, current_user: User = Depends(get_current_user)
):
    """Retrieve a specific medical record"""
    try:
        record = data_manager.get_record(
            current_user.username, int(record_id), current_user.username, "API access"
        )
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health-analysis/{patient_id}")
async def get_health_analysis(
    patient_id: str, current_user: User = Depends(get_current_user)
):
    """Get AI-powered health analysis"""
    try:
        patient_history = data_manager.get_patient_history(
            patient_id, current_user.username
        )
        if not patient_history:
            raise HTTPException(status_code=404, detail="No records found")

        analysis = health_analyzer.analyze_trends(patient_history)
        recommendations = health_analyzer.generate_health_recommendations(analysis)

        return {"analysis": analysis, "recommendations": recommendations}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/access-control/{patient_id}/{accessor_id}")
async def manage_access_control(
    patient_id: str,
    accessor_id: str,
    grant: bool,
    current_user: User = Depends(get_current_user),
):
    """Manage access control for medical records"""
    if current_user.username != patient_id:
        raise HTTPException(
            status_code=403, detail="Only the patient can manage their access controls"
        )

    try:
        if grant:
            data_manager.grant_access(patient_id, accessor_id)
        else:
            data_manager.revoke_access(patient_id, accessor_id)
        return {"status": "success", "action": "granted" if grant else "revoked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/access-log/{patient_id}")
async def get_access_logs(
    patient_id: str, current_user: User = Depends(get_current_user)
):
    """Get access logs for medical records"""
    try:
        logs = data_manager.get_access_log(patient_id, current_user.username)
        return {"access_logs": logs}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
