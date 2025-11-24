from sqlalchemy import insert
from app.core.database import engine_sync, engine_txonly, get_db, get_db_txonly    
from app.models.profile import Profile
from app.utils.database import map_to_pydantic
from app.utils.logger import log_api

# When to Use Engine

#     Direct SQL execution: When you need to execute raw SQL or have complex queries
#     Bulk operations: For inserting or updating thousands of records at once
#     Data migration scripts: For ETL processes and database migrations
#     Performance-critical operations: When you need maximum performance
#     Simple database interactions: For straightforward queries without complex relationships

# When to Use SessionMaker

#     Application business logic: For most application code dealing with domain objects
#     Complex object relationships: When managing related objects and their relationships
#     CRUD operations: For creating, reading, updating, and deleting individual records
#     Change tracking: When you need to track changes to objects
#     Transaction management: For operations that need to be atomic


class ProfileService:
    def __init__(self):
        self.engine_sync = engine_sync
        self.engine_txonly = engine_txonly
        self.db = get_db()
        self.db_txonly = get_db_txonly()

    def create_profile(self, profile: Profile) -> tuple[Profile | None, str | None]:
        try:
            self.db_txonly.add(profile)
            self.db_txonly.commit()
            self.db_txonly.refresh(profile)
            return profile, None
        except Exception as e:
            log_api(f"Error creating profile: {e}", act="profile", level="ERROR")
            return None, str(e)

    def bulk_create_profiles(self, profiles: list[Profile]) -> tuple[list[Profile] | None, str | None]:
        try:
            self.db_txonly.add_all(profiles)
            self.db_txonly.commit()
            self.db_txonly.refresh_all(profiles)
            return profiles, None
        except Exception as e:
            log_api(f"Error bulk creating profiles: {e}", act="profile", level="ERROR")
            return None, str(e)

    def get_profile(self, profile_id: int) -> tuple[Profile | None, str | None]:
        try:
            profile = self.db_txonly.query(Profile).filter(Profile.id == profile_id).first()
            return profile, None
        except Exception as e:
            log_api(f"Error getting profile: {e}", act="profile", level="ERROR")
            return None, str(e)

    def get_profiles(self) -> tuple[list[Profile] | None, str | None]:
        try:
            profiles = self.db_txonly.query(Profile).filter(Profile.is_active == True).all()
            return profiles, None
        except Exception as e:
            log_api(f"Error getting profiles: {e}", act="profile", level="ERROR")
            return None, str(e)

    # def get_profiles1(self):
    #     try:
    #         query = select(Profile).where(Profile.is_active == True)
    #         with self.engine_sync.connect() as conn:
    #             result = conn.execute(query)
    #             res_data = result.first()
    #             user = map_to_pydantic(res_data, UserLoginResponse) if res_data else None
    #             return user
    #     except Exception as e:
    #         log_api(f"Error loading user {id}: {e}", act="auth", level="ERROR")
    #         return None