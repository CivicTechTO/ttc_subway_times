--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.1
-- Dumped by pg_dump version 9.6.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
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
    train_message text,
    train_dest text
);


--
-- Name: polls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE polls (
    pollid integer NOT NULL,
    poll_start timestamp without time zone,
    poll_end timestamp without time zone
);


--
-- Name: polls_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE polls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: polls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE polls_id_seq OWNED BY polls.pollid;


--
-- Name: requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE requests (
    requestid bigint NOT NULL,
    data_ text,
    stationid integer NOT NULL,
    lineid integer NOT NULL,
    all_stations text,
    create_date timestamp without time zone,
    pollid integer,
    request_date timestamp without time zone
);


--
-- Name: requests_requestid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE requests_requestid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: requests_requestid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE requests_requestid_seq OWNED BY requests.requestid;


--
-- Name: polls pollid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY polls ALTER COLUMN pollid SET DEFAULT nextval('polls_id_seq'::regclass);


--
-- Name: requests requestid; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY requests ALTER COLUMN requestid SET DEFAULT nextval('requests_requestid_seq'::regclass);


--
-- Name: polls polls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY polls
    ADD CONSTRAINT polls_pkey PRIMARY KEY (pollid);


--
-- PostgreSQL database dump complete
--

