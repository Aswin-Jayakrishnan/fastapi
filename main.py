from fastapi import FastAPI,HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship,joinedload

from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional

Db_URL = "postgresql://postgres:pgadmin@localhost/postgres"
engine = create_engine(Db_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    phone = Column(String, unique=True)

    profile = relationship("Profile", uselist=False, back_populates="user")


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="profile")




app = FastAPI()


Base.metadata.create_all(bind=engine)


class sampleBaseModel(BaseModel):
    full_name: str
    email: str
    password: str
    phone: str
    profile_picture: str



@app.post("/register")
async def register_user(user_data: sampleBaseModel):
  
    db = SessionLocal()
    res = db.query(User).filter(User.email == user_data.email or User.phone == user_data.phone).first()

    if res:
        return {"error": "Email or phone already exists."}

   
    # new_user = User(full_name=user.full_name, email=user.email, password=user.password, phone=user.phone)
    # db.add(new_user)
    # db.commit()
    # # db.refresh(new_user)

    # profile_picture = Profile(profile_picture=user.profile_picture)
    # user.profile_picture = profile_picture
    # db.add(new_user)
    # db.commit()
    # # db.refresh(new_profile)

    # db.close()


    
    # Create user object
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=user_data.password,
        phone=user_data.phone,
    )

   
    profile = Profile(profile_picture=user_data.profile_picture)
    user.profile = profile

 
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully"}


#get the specific user by passing id

@app.get("/getuser/{user_id}")
def get_user_details(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "profile_picture": user.profile.profile_picture if user.profile else None,
    }



# get all users 

@app.get("/getall_users")
def get_all_users():
    db = SessionLocal()
    users = db.query(User).all()

    user_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "profile_picture": user.profile.profile_picture if user.profile else None,
        }
        user_list.append(user_data)

    return user_list