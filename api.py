from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, Propriete
from auth import verify_password, create_token, get_current_user, admin_required, users_db

app = FastAPI(title="Virtual SN 360", description="Plateforme de visite virtuelle 3D - Sénégal", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProprieteCreate(BaseModel):
    type: str
    nom: str
    ville: str
    prix: float
    surface: int
    disponible: bool = True

class ProprieteUpdate(BaseModel):
    type: Optional[str] = None
    nom: Optional[str] = None
    ville: Optional[str] = None
    prix: Optional[float] = None
    surface: Optional[int] = None
    disponible: Optional[bool] = None

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form.username)
    if not user or not verify_password(form.password, user["password"]):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    token = create_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
def accueil():
    return {"app": "Virtual SN 360", "message": "Bienvenue sur la plateforme de visite virtuelle 3D", "version": "1.0.0"}

@app.get("/proprietes")
def get_proprietes(db: Session = Depends(get_db)):
    return db.query(Propriete).all()

@app.get("/proprietes/{id}")
def get_propriete(id: int, db: Session = Depends(get_db)):
    propriete = db.query(Propriete).filter(Propriete.id == id).first()
    if propriete:
        return propriete
    raise HTTPException(status_code=404, detail="Propriété non trouvée")

@app.get("/type/{type_bien}")
def get_par_type(type_bien: str, db: Session = Depends(get_db)):
    return db.query(Propriete).filter(Propriete.type == type_bien).all()

@app.get("/ville/{ville}")
def get_par_ville(ville: str, db: Session = Depends(get_db)):
    return db.query(Propriete).filter(Propriete.ville == ville).all()

@app.get("/statistiques")
def get_statistiques(db: Session = Depends(get_db)):
    return {
        "total": db.query(Propriete).count(),
        "maisons": db.query(Propriete).filter(Propriete.type == "Maison").count(),
        "centres_commerciaux": db.query(Propriete).filter(Propriete.type == "Centre Commercial").count(),
        "usines": db.query(Propriete).filter(Propriete.type == "Usine").count(),
        "disponibles": db.query(Propriete).filter(Propriete.disponible == True).count()
    }

@app.get("/profil")
def get_profil(user=Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}

@app.post("/proprietes")
def creer_propriete(propriete: ProprieteCreate, db: Session = Depends(get_db), user=Depends(admin_required)):
    nouvelle = Propriete(**propriete.model_dump())
    db.add(nouvelle)
    db.commit()
    db.refresh(nouvelle)
    return {"message": "Propriété créée avec succès", "propriete": nouvelle}

@app.put("/proprietes/{id}")
def modifier_propriete(id: int, data: ProprieteUpdate, db: Session = Depends(get_db), user=Depends(admin_required)):
    propriete = db.query(Propriete).filter(Propriete.id == id).first()
    if not propriete:
        raise HTTPException(status_code=404, detail="Propriété non trouvée")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(propriete, key, value)
    db.commit()
    db.refresh(propriete)
    return {"message": "Propriété modifiée avec succès", "propriete": propriete}

@app.delete("/proprietes/{id}")
def supprimer_propriete(id: int, db: Session = Depends(get_db), user=Depends(admin_required)):
    propriete = db.query(Propriete).filter(Propriete.id == id).first()
    if not propriete:
        raise HTTPException(status_code=404, detail="Propriété non trouvée")
    db.delete(propriete)
    db.commit()
    return {"message": f"Propriété supprimée avec succès"}