--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.5
-- Dumped by pg_dump version 9.5.5

-- Started on 2017-02-05 23:10:21 EST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 1 (class 3079 OID 12990)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2742 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 183 (class 1259 OID 22878)
-- Name: ntas_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE ntas_data (
    requestid bigint,
    id bigint,
    station_char text,
    subwayline text,
    system_message_type text,
    timint numeric,
    traindirection text,
    trainid integer,
    train_message text
);


--
-- TOC entry 182 (class 1259 OID 22871)
-- Name: requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE requests (
    requestid bigint NOT NULL,
    data_ text,
    stationid integer NOT NULL,
    lineid integer NOT NULL,
    all_stations text,
    create_date timestamp without time zone
);


--
-- TOC entry 181 (class 1259 OID 22869)
-- Name: requests_requestid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE requests_requestid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2743 (class 0 OID 0)
-- Dependencies: 181
-- Name: requests_requestid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE requests_requestid_seq OWNED BY requests.requestid;


--
-- TOC entry 2620 (class 2604 OID 22874)
-- Name: requestid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY requests ALTER COLUMN requestid SET DEFAULT nextval('requests_requestid_seq'::regclass);


--
-- TOC entry 2741 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2017-02-05 23:10:21 EST

--
-- PostgreSQL database dump complete
--

