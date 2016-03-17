from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, BigInteger, String, Numeric, ForeignKey
from sqlalchemy.orm import mapper, relationship
from geoalchemy2 import Geometry, Geography

DATABASE_NAME = "usgs_seismology"

Base = declarative_base()

earthquake_fault_association_table = Table('earthquake_fault', Base.metadata,
    Column('earthquake_id', Integer, ForeignKey('earthquake.id')),
    Column('fault_id', Integer, ForeignKey('fault.id')),
    Column('confidence', Numeric)
)

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
	faults = relationship("Fault", secondary=earthquake_fault_association_table, back_populates="earthquakes")

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
	nodalPlane1Dip = Column(String)
	nodalPlane1Rake = Column(String)
	nodalPlane1Strike = Column(String)
	nodalPlane2Dip = Column(String)
	nodalPlane2Rake = Column(String)
	nodalPlane2Strike = Column(String)
	latitude = Column(String)
	longitude = Column(String)
	depth = Column(String)
	reviewStatus = Column(String)
	evaluationStatus = Column(String)
	numStationsUsed = Column(String)
	source = Column(String)
	eventsource = Column(String)
	eventsourcecode = Column(String)
	eventtime = Column(String)
	eventParametersPublicID = Column(String)
	quakemlPublicid = Column(String)
	earthquake = relationship("Earthquake", back_populates="focalMechanisms")

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
	geometry = Column(Geometry)
	earthquakes = relationship("Earthquake", secondary=earthquake_fault_association_table, back_populates="faults")
