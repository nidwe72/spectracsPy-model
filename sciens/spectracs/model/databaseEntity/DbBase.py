

from appdata import AppDataPaths
from sqlalchemy import \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.schema import Column
from sqlalchemy.sql.sqltypes import String
from sqlalchemy_serializer import SerializerMixin

from sciens.base.Singleton import Singleton

import uuid

app_paths = AppDataPaths()
app_paths.setup()

dbFilepath='sqlite:///'+app_paths.app_data_path+'/spectracsPy.db'
engine = create_engine(dbFilepath)

_SessionFactory = sessionmaker(bind=engine,expire_on_commit=False)

# A separate factory for SHORT-LIVED sessions used to persist an object graph (workflow save/update/delete).
# autoflush=False so ONLY an explicit add()+commit() writes — a transient/half-built graph held elsewhere in
# the app can never be dragged in by an unrelated query, the way the shared singleton session would
# (SPEC_workflow_persistence.md §2.2). The caller owns the lifecycle: get it, use it, close() it.
_SaveSessionFactory = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

DbBaseEntity = declarative_base()

def session_factory()->Session:
    DbBaseEntity.metadata.create_all(engine)
    return SessionProvider().getSession()

def save_session()->Session:
    # A fresh, short-lived, autoflush-OFF session for persisting/updating/deleting a workflow graph.
    DbBaseEntity.metadata.create_all(engine)
    return _SaveSessionFactory()


def to_underscore(name):
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_guid():
    result=uuid.uuid4()
    print('#####get_guid#####')
    print (result)
    return result

@declarative_mixin
class DbBaseEntityMixin(SerializerMixin):
    __table_args__ = {'extend_existing': True}
    @declared_attr
    def __tablename__(cls):
        result=to_underscore(cls.__name__)
        # print (result)
        return result


    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))


class SessionProvider(Singleton):
    session=None

    def getSession(self):
        if self.session is None:
            self.session=_SessionFactory()
        return self.session

