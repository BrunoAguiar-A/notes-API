from passlib.context import CryptContext

# Cripting psw by bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    return fake_users_db.get(username)
# bd user
fake_users_db = {
    "bruno": {
        "username": "bruno",
        "hashed_password": "$2b$12$rVVWiS/BKS2qeJsGsWwS1usHmI1mSQ.yTqzMi3d0ZR41.GVTmlFn6",  # pwd: 123456
    },
    "usuario_teste": {
        "username": "usuario_teste",
        "hashed_password": get_password_hash("senha123"),
    }
}