"""Initialise les données de référence : rôles, catégories, régions/villes, paramètres et compte administrateur.

Usage : python -m app.scripts.seed
Idempotent : peut être relancé sans créer de doublons. Aucune donnée fictive d'utilisateur ou d'annonce.
"""
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.domain.entities.enums import RoleName, UserStatus
from app.domain.services.compatibility import CompatibilityWeights
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.models.geo import CityModel, PropertyCategoryModel, RegionModel
from app.infrastructure.models.user import (
    ApplicationSettingModel, RoleModel, UserModel, UserProfileModel, UserRoleModel,
)

CATEGORIES = ["Appartement", "Maison", "Villa", "Studio", "Chambre"]
# Régions (gouvernorats de Tunisie) et principales villes : modifiables depuis l'espace administrateur.
REGIONS = {
    "Tunis": ["Tunis", "Carthage", "La Marsa", "Le Bardo", "La Goulette", "Sidi Bou Saïd"],
    "Ariana": ["Ariana", "La Soukra", "Raoued", "Ettadhamen"],
    "Ben Arous": ["Ben Arous", "Radès", "Hammam Lif", "Mégrine"],
    "Manouba": ["La Manouba", "Denden", "Oued Ellil"],
    "Nabeul": ["Nabeul", "Hammamet", "Kélibia", "Korba"],
    "Zaghouan": ["Zaghouan"],
    "Bizerte": ["Bizerte", "Menzel Bourguiba"],
    "Béja": ["Béja"], "Jendouba": ["Jendouba", "Tabarka"], "Le Kef": ["Le Kef"], "Siliana": ["Siliana"],
    "Sousse": ["Sousse", "Hammam Sousse", "Kantaoui"],
    "Monastir": ["Monastir", "Skanes", "Ksar Hellal"],
    "Mahdia": ["Mahdia"],
    "Sfax": ["Sfax"],
    "Kairouan": ["Kairouan"], "Kasserine": ["Kasserine"], "Sidi Bouzid": ["Sidi Bouzid"],
    "Gabès": ["Gabès"], "Médenine": ["Médenine", "Djerba Houmt Souk", "Zarzis"], "Tataouine": ["Tataouine"],
    "Gafsa": ["Gafsa"], "Tozeur": ["Tozeur"], "Kébili": ["Kébili"],
}


def run() -> None:
    with SessionLocal() as db:
        roles = {}
        for r in RoleName:
            obj = db.execute(select(RoleModel).where(RoleModel.name == r.value)).scalars().first() or RoleModel(name=r.value)
            db.add(obj)
            roles[r.value] = obj
        for name in CATEGORIES:
            if not db.execute(select(PropertyCategoryModel).where(PropertyCategoryModel.name == name)).scalars().first():
                db.add(PropertyCategoryModel(name=name))
        db.flush()
        for region_name, cities in REGIONS.items():
            region = db.execute(select(RegionModel).where(RegionModel.name == region_name)).scalars().first()
            if not region:
                region = RegionModel(name=region_name)
                db.add(region)
                db.flush()
            for c in cities:
                if not db.execute(select(CityModel).where(CityModel.region_id == region.id, CityModel.name == c)).scalars().first():
                    db.add(CityModel(region_id=region.id, name=c))
        for name in CompatibilityWeights.__dataclass_fields__:
            key = f"compat_weight_{name}"
            if not db.execute(select(ApplicationSettingModel).where(ApplicationSettingModel.key == key)).scalars().first():
                db.add(ApplicationSettingModel(key=key, value=str(getattr(CompatibilityWeights(), name))))
        db.flush()

        if settings.admin_password:
            email = settings.admin_email.lower()
            admin = db.execute(select(UserModel).where(UserModel.email == email)).scalars().first()
            if not admin:
                admin = UserModel(email=email, password_hash=hash_password(settings.admin_password), status=UserStatus.ACTIVE)
                db.add(admin)
                db.flush()
                db.add(UserProfileModel(user_id=admin.id, first_name="Admin", last_name="DarMate"))
                db.add(UserRoleModel(user_id=admin.id, role_id=roles[RoleName.ADMIN.value].id))
                print(f"Administrateur créé : {email}")
            else:
                print(f"Administrateur déjà présent : {email}")
        else:
            print("ADMIN_PASSWORD non défini : aucun administrateur créé.")
        db.commit()
    print("Données de référence prêtes.")


if __name__ == "__main__":
    run()
