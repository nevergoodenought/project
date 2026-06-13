-- Table kerch
CREATE TABLE "kerch"
(
  "idkword" integer NOT NULL,
  "ruwordkerch" character varying,
  "ruswordkerch" character varying,
  "idrusword" integer NOT NULL,
  CONSTRAINT "pk_kerch" PRIMARY KEY ("idkword", "idrusword")
)
WITH (autovacuum_enabled=true);

-- Table pop_rus_ua_ru
CREATE TABLE "pop_rus_ua_ru"
(
  "idpopword" integer NOT NULL,
  "ruwordpop" character varying,
  "ruswordpop" character varying,
  "uawordpop" character varying,
  "idrusword" integer NOT NULL,
  CONSTRAINT "pk_pop_rus_ua_ru" PRIMARY KEY ("idpopword", "idrusword")
)
WITH (autovacuum_enabled=true);

-- Table mirinov
CREATE TABLE "mirinov"
(
  "idmword" integer NOT NULL,
  "ruswordm" character varying,
  "ruwordm" character varying,
  "idrusword" integer NOT NULL,
  CONSTRAINT "pk_mirinov" PRIMARY KEY ("idmword", "idrusword")
)
WITH (autovacuum_enabled=true);

-- Table rusword
CREATE TABLE "rusword"
(
  "idrusword" SERIAL NOT NULL,
  "rusword" character varying,
  CONSTRAINT "pk_rusword" PRIMARY KEY ("idrusword")
)
WITH (autovacuum_enabled=true);


-- Foreign keys
ALTER TABLE "kerch" ADD CONSTRAINT "ruskerch" 
  FOREIGN KEY ("idrusword") REFERENCES "rusword" ("idrusword");

ALTER TABLE "mirinov" ADD CONSTRAINT "rusmironov" 
  FOREIGN KEY ("idrusword") REFERENCES "rusword" ("idrusword");

ALTER TABLE "pop_rus_ua_ru" ADD CONSTRAINT "ruspop" 
  FOREIGN KEY ("idrusword") REFERENCES "rusword" ("idrusword");


