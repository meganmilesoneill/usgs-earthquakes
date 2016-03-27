from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, BigInteger, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import mapper, relationship
from geoalchemy2 import Geometry, Geography


Base = declarative_base()


class Earthquake(Base):
    __tablename__ = "earthquake"

    id = Column(Integer, primary_key=True)
    eventid = Column(String)
    mag = Column(Numeric)
    place = Column(String)
    time = Column(BigInteger)
    updated = Column(BigInteger)
    tz = Column(Integer)
    url = Column(String)
    detail = Column(String)
    felt = Column(BigInteger)
    cdi = Column(Numeric)
    mmi = Column(Numeric)
    alert = Column(String)
    status = Column(String)
    tsunami = Column(BigInteger)
    sig = Column(BigInteger)
    net = Column(String)
    code = Column(String)
    ids = Column(String)
    sources = Column(String)
    types = Column(String)
    nst = Column(BigInteger)
    dmin = Column(Numeric)
    rml = Column(Numeric)
    gap = Column(Numeric)
    magType = Column(String)
    eventType = Column(String)
    title = Column(String)
    geometry = Column(Geography)
    origins = relationship("Origin", back_populates='earthquake', cascade="all, delete, delete-orphan")
    focalMechanisms = relationship("FocalMechanism", back_populates='earthquake', cascade="all, delete, delete-orphan")
    momentTensors = relationship("MomentTensor", back_populates='earthquake', cascade="all, delete, delete-orphan")
    faults = relationship("Fault", secondary='earthquake_fault', back_populates="earthquakes")

    def setPrimaryProducts(self, session):
        focalMechanisms = session.query(FocalMechanism).filter_by(earthquake_id = self.id).order_by(FocalMechanism.preferredWeight.desc(), FocalMechanism.updateTime.desc())
        is_first = True
        for focalMechanism in focalMechanisms:
            focalMechanism.is_primary = is_first
            is_first = False

        momentTensors = session.query(MomentTensor).filter_by(earthquake_id = self.id).order_by(MomentTensor.preferredWeight.desc(), MomentTensor.updateTime.desc())
        is_first = True
        for momentTensor in momentTensors:
            momentTensor.is_primary = is_first
            is_first = False

        session.commit()

    def setNearestFaults(self, session, distance):
        session.execute(
            "INSERT INTO earthquake_fault (earthquake_id, fault_id, distance) SELECT e.id, f.id, ST_Distance(e.geometry, f.geometry) FROM earthquake e, fault f WHERE ST_DWithin(e.geometry, f.geometry, :distance) AND e.id = :earthquake_id",
            {"distance": distance, "earthquake_id": self.id}
        )
        session.commit();

class Origin(Base):
    __tablename__ = "earthquake_origin"

    id = Column(Integer, primary_key=True)
    earthquake_id = Column(Integer, ForeignKey("earthquake.id"))
    code = Column(String, nullable=True)
    earthquake = relationship("Earthquake", back_populates="origins")

class FocalMechanism(Base):
    __tablename__ = "earthquake_focal_mechanism"

    id = Column(Integer, primary_key=True)
    earthquake_id = Column(Integer, ForeignKey("earthquake.id"))
    code = Column(String)
    preferredWeight = Column(Numeric)
    indexid = Column(BigInteger)
    indexTime = Column(BigInteger)
    updateTime = Column(BigInteger)
    status = Column(String)
    beachballSource = Column(String)
    nodalPlane1Dip = Column(Numeric)
    nodalPlane1Rake = Column(Numeric)
    nodalPlane1Strike = Column(Numeric)
    nodalPlane2Dip = Column(Numeric)
    nodalPlane2Rake = Column(Numeric)
    nodalPlane2Strike = Column(Numeric)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    depth = Column(Numeric)
    reviewStatus = Column(String)
    evaluationStatus = Column(String)
    numStationsUsed = Column(String)
    source = Column(String)
    eventsource = Column(String)
    eventsourcecode = Column(String)
    eventtime = Column(String)
    eventParametersPublicID = Column(String)
    quakemlPublicid = Column(String)
    is_primary = Column(Boolean, default=False)
    earthquake = relationship("Earthquake", back_populates="focalMechanisms")

class MomentTensor(Base):
    __tablename__ = "earthquake_moment_tensor"

    id = Column(Integer, primary_key=True)
    earthquake_id = Column(Integer, ForeignKey("earthquake.id"))
    code = Column(String)
    preferredWeight = Column(Numeric)
    indexid = Column(BigInteger)
    indexTime = Column(BigInteger)
    updateTime = Column(BigInteger)
    status = Column(String)
    beachballSource = Column(String)
    beachballType = Column(String)
    nAxisAzimuth = Column(Numeric)
    nAxisLength = Column(Numeric)
    nAxisPlunge = Column(Numeric)
    pAxisAzimuth = Column(Numeric)
    pAxisLength = Column(Numeric)
    pAxisPlunge = Column(Numeric)
    tAxisAzimuth = Column(Numeric)
    tAxisLength = Column(Numeric)
    tAxisPlunge = Column(Numeric)
    nodalPlane1Dip = Column(Numeric)
    nodalPlane1Rake = Column(Numeric)
    nodalPlane1Strike = Column(Numeric)
    nodalPlane2Dip = Column(Numeric)
    nodalPlane2Rake = Column(Numeric)
    nodalPlane2Strike = Column(Numeric)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    depth = Column(Numeric)
    reviewStatus = Column(String)
    evaluationStatus = Column(String)
    numStationsUsed = Column(String)
    source = Column(String)
    scalarMoment = Column(Numeric)
    sourcetimeDuration = Column(Numeric)
    sourcetimeType = Column(String)
    eventsource = Column(String)
    eventsourcecode = Column(String)
    eventtime = Column(String)
    eventParametersPublicID = Column(String)
    quakemlPublicid = Column(String)
    mrr = Column(Numeric)
    mtt = Column(Numeric)
    mpp = Column(Numeric)
    mrt = Column(Numeric)
    mrp = Column(Numeric)
    mtp = Column(Numeric)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    depth = Column(Numeric)
    is_primary = Column(Boolean, default=False)
    earthquake = relationship("Earthquake", back_populates="momentTensors")


class Fault(Base):
    __tablename__ = "fault"

    id = Column(Integer, primary_key=True)
    faultid = Column(String)
    sectionid = Column(String)
    name = Column(String)
    fcode = Column(Integer)
    slipdirect = Column(String)
    slipsense = Column(String)
    slipcode = Column(Integer)
    sliprate = Column(String)
    length = Column(Numeric)
    agecat = Column(String)
    age = Column(BigInteger)
    objectid = Column(BigInteger)
    facode = Column(String)
    mappedscal = Column(String)
    ftype = Column(String)
    dipdirecti = Column(String)
    num = Column(String)
    secondaries = Column(String)
    cooperator = Column(String)
    acode = Column(Integer)
    azimuth = Column(Integer)
    url = Column(String)
    code = Column(BigInteger)
    geometry = Column(Geography)
    earthquakes = relationship("Earthquake", secondary='earthquake_fault', back_populates="faults")

    def setNearestEarthquakes(self, session, distance):
        session.execute(
            "INSERT INTO earthquake_fault (earthquake_id, fault_id, distance) SELECT e.id, f.id, ST_Distance(e.geometry, f.geometry) FROM earthquake e, fault f WHERE ST_DWithin(e.geometry, f.geometry, :distance) AND f.id = :fault_id",
            {"distance": distance, "fault_id": self.id}
        )
        session.commit();

class EarthquakeFaultLink(Base):
    __tablename__ = "earthquake_fault"

    earthquake_id = Column(Integer, ForeignKey("earthquake.id"), primary_key=True)
    fault_id = Column(Integer, ForeignKey("fault.id"), primary_key=True)
    distance = Column(Numeric)
    confidence = Column(Numeric)
    earthquake = relationship(Earthquake, backref=backref("earthquake_assoc"))
    fault = relationship(Fault, backref=backref("fault_assoc"))
