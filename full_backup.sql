--
-- PostgreSQL database dump
--

\restrict j05DURLF8eejtLNwejvhc4oL4XyGtmRFsFKf4yAArlydmy5xV5EMJHt2v9kXo7P

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Type: SCHEMA; Schema: -; Owner: postgres
--

--CREATE SCHEMA tenant_03118c02_f589_49fb_a4ea_f86a867a72b6;


--ALTER SCHEMA tenant_03118c02_f589_49fb_a4ea_f86a867a72b6 OWNER TO postgres;

--
-- Name: timetracker; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA timetracker;


ALTER SCHEMA timetracker OWNER TO postgres;

--
-- Name: time_entry_status; Type: TYPE; Schema: timetracker; Owner: postgres
--

CREATE TYPE timetracker.time_entry_status AS ENUM (
    'submitted',
    'approved',
    'rejected'
);


ALTER TYPE timetracker.time_entry_status OWNER TO postgres;

--
-- Name: update_timestamp(); Type: FUNCTION; Schema: timetracker; Owner: postgres
--

CREATE FUNCTION timetracker.update_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;


ALTER FUNCTION timetracker.update_timestamp() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: fordel_t; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fordel_t (
    id numeric,
    level "char"
);


ALTER TABLE public.fordel_t OWNER TO postgres;

--
-- Name: test; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.test (
    codet integer,
    namet character varying
);


ALTER TABLE public.test OWNER TO postgres;

--
-- Name: timetrackercompanies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.timetrackercompanies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    address text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.timetrackercompanies OWNER TO postgres;

--
-- Name: absences; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

/*CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.absences (
    id character varying(50) NOT NULL,
    user_id character varying(50) NOT NULL,
    absence_type character varying(20) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    note text,
    is_approved boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.absences OWNER TO postgres;

--
-- Name: audit_logs; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.audit_logs (
    id character varying(36) NOT NULL,
    admin_id character varying(36),
    action_type character varying(100) NOT NULL,
    target_type character varying(100),
    target_id character varying(36),
    details text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.audit_logs OWNER TO postgres;

--
-- Name: breaks; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.breaks (
    id character varying(50) NOT NULL,
    time_entry_id character varying(50),
    start_time bigint NOT NULL,
    end_time bigint,
    duration integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.breaks OWNER TO postgres;

--
-- Name: clients; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.clients (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255),
    phone character varying(50),
    address text,
    tax_id character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.clients OWNER TO postgres;

--
-- Name: daily_summaries; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.daily_summaries (
    id character varying(50) NOT NULL,
    user_id character varying(50) NOT NULL,
    work_date date NOT NULL,
    total_work_minutes integer DEFAULT 0,
    total_break_minutes integer DEFAULT 0,
    is_approved boolean DEFAULT false,
    approved_by character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.daily_summaries OWNER TO postgres;

--
-- Name: projects; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.projects (
    id uuid NOT NULL,
    company_id uuid NOT NULL,
    client_id uuid,
    name character varying(255) NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.projects OWNER TO postgres;

--
-- Name: time_entries; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.time_entries (
    id character varying(50) NOT NULL,
    user_id character varying(50),
    project_id uuid NOT NULL,
    project_name character varying(255) NOT NULL,
    client_name character varying(255),
    start_time bigint NOT NULL,
    end_time bigint,
    duration integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    is_manual boolean,
    approval_status character varying(20) DEFAULT 'approved'::character varying,
    note character varying(255),
    synced_at timestamp with time zone DEFAULT now()
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.time_entries OWNER TO postgres;

--
-- Name: user_projects; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects (
    id integer NOT NULL,
    user_id character varying(255) NOT NULL,
    project_id character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects OWNER TO postgres;

--
-- Name: user_projects_id_seq; Type: SEQUENCE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE SEQUENCE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects_id_seq OWNER TO postgres;

--
-- Name: user_projects_id_seq; Type: SEQUENCE OWNED BY; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER SEQUENCE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects_id_seq OWNED BY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects.id;


--
-- Name: users; Type: TABLE; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

CREATE TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.users (
    id character varying(50) NOT NULL,
    email character varying(255),
    full_name character varying(255),
    role character varying(50) DEFAULT 'employee'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    password_hash character varying(255),
    include_in_reports boolean DEFAULT true
);


ALTER TABLE tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.users OWNER TO postgres;
*/
--
-- Name: activation_tokens; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.activation_tokens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_user_id uuid NOT NULL,
    token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at time with time zone
);


ALTER TABLE timetracker.activation_tokens OWNER TO postgres;

--
-- Name: active_sessions; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.active_sessions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid NOT NULL,
    project_id uuid NOT NULL,
    company_user_id uuid NOT NULL,
    start_time timestamp with time zone NOT NULL,
    is_manual boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE timetracker.active_sessions OWNER TO postgres;

--
-- Name: clients; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.clients (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    address text,
    contact_name character varying(255),
    contact_email character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE timetracker.clients OWNER TO postgres;

--
-- Name: companies; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.companies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    address text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE timetracker.companies OWNER TO postgres;

--
-- Name: company_users; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.company_users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid NOT NULL,
    user_id uuid NOT NULL,
    status character varying(50) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    role character varying(100)
);


ALTER TABLE timetracker.company_users OWNER TO postgres;

--
-- Name: project_assignments; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.project_assignments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    company_user_id uuid NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE timetracker.project_assignments OWNER TO postgres;

--
-- Name: projects; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.projects (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    client_id uuid
);


ALTER TABLE timetracker.projects OWNER TO postgres;

--
-- Name: time_entries; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.time_entries (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    company_id uuid NOT NULL,
    project_id uuid NOT NULL,
    company_user_id uuid NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone NOT NULL,
    duration_minutes integer NOT NULL,
    status timetracker.time_entry_status DEFAULT 'submitted'::timetracker.time_entry_status NOT NULL,
    is_manual boolean DEFAULT false NOT NULL,
    is_over_limit boolean DEFAULT false NOT NULL,
    justification_note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE timetracker.time_entries OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: timetracker; Owner: postgres
--

CREATE TABLE timetracker.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(255),
    display_name character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    password_hash character varying(255),
    is_active boolean DEFAULT true
);


ALTER TABLE timetracker.users OWNER TO postgres;

--
-- Name: user_projects id; Type: DEFAULT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

--ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects ALTER COLUMN id SET DEFAULT nextval('tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects_id_seq'::regclass);


--
-- Data for Name: fordel_t; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.fordel_t (id, level) FROM stdin;
\.


--
-- Data for Name: test; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.test (codet, namet) FROM stdin;
\.


--
-- Data for Name: timetrackercompanies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.timetrackercompanies (id, name, address, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: absences; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--
/*
COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.absences (id, user_id, absence_type, start_date, end_date, note, is_approved, created_at) FROM stdin;
abs_5f6bb79a423d	usr_default	urlaub	2026-11-02	2026-11-02	Hffh	t	2026-11-02 21:01:00.821995+01
abs_f6f9cd931b9d	usr_default	krankheit	2025-11-03	2026-11-04		f	2026-11-15 20:26:20.202756+01
abs_61e404f3707a	usr_default	krankheit	2026-11-03	2026-11-04		f	2026-11-15 20:24:59.630371+01
abs_d2a3abeb5ec8	usr_default	urlaub	2026-11-15	2026-11-15	Bb	f	2026-11-15 21:25:51.47585+01
abs_eee3c2f02e57	usr_default	krankheit	2026-11-16	2026-11-16	Vcx	t	2026-11-15 21:26:19.659563+01
abs_001c80a15a19	usr_default	krankheit	2026-11-17	2026-11-17	Gxg	f	2026-11-15 21:33:06.100716+01
abs_cf45ce064c22	usr_default	urlaub	2026-11-18	2026-11-18	Gv	t	2026-11-15 21:44:21.142044+01
abs_bf7aa25b4da2	usr_default	urlaub	2026-11-20	2026-11-28		f	2026-11-15 21:46:04.598773+01
abs_40d2c762b57b	usr_default	krankheit	2026-11-14	2026-11-15		t	2026-11-15 21:45:24.028495+01
abs_5e8cef18053e	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	urlaub	2026-11-21	2026-11-21	Ggc	t	2026-11-15 22:04:48.825028+01
abs_11ea739d79e9	usr_default	urlaub	2026-11-19	2026-11-19	Fcc	f	2026-11-15 21:50:24.372899+01
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.audit_logs (id, admin_id, action_type, target_type, target_id, details, created_at) FROM stdin;
4b23ce9b-d4c0-419e-bd35-0fddbbab39de	admin_user	UPDATE_USER_REPORT_STATUS	USER	0ab9edff-aa40-48f8-915d-068a164e59e8	Changed include_in_reports to False	2026-11-01 17:06:52.233182
c9c440ac-9d7a-4d23-9ceb-2d4362bdbfbb	admin_user	UPDATE_USER_REPORT_STATUS	USER	0ab9edff-aa40-48f8-915d-068a164e59e8	Changed include_in_reports to True	2026-11-01 17:08:34.689568
5b91a7c6-cce0-44eb-8d02-be2ca64a9726	admin_user	APPROVE_AND_EDIT_TIME_ENTRY	TIME_ENTRY	3d6d3cf2-31fc-4190-9e39-bc54d90b0dda	Status changed from pending to approved | Duration changed from 1074 to 50	2026-11-14 13:07:52.060088
07bddae2-c115-4147-b0ca-ed1e3ef152b6	admin_user	APPROVE_AND_EDIT_TIME_ENTRY	TIME_ENTRY	8de1ef23-eab4-4cba-aa7a-3462cc28ed1e	Status changed from pending to approved | Duration changed from 63 to 61 | Project changed to Test N1 p1	2026-11-14 13:16:16.898977
\.


--
-- Data for Name: breaks; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.breaks (id, time_entry_id, start_time, end_time, duration, created_at) FROM stdin;
manual_break_1	226b0b07-8b99-4b06-a724-8059dcce0897	1793602848000	1793605848000	50	2026-11-02 16:50:50.616811+01
\.


--
-- Data for Name: clients; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.clients (id, name, email, phone, address, tax_id, created_at, updated_at) FROM stdin;
4da054bc-9ac3-4aee-8740-d9e82d514e1f	Hhfgg	amir_amarloo@yahoo.comvvvv	+98 21 8888 19665555	The	Yyy	2026-10-29 16:41:35.711317+01	2026-10-29 16:41:35.711317+01
a8fc1985-ed9f-4618-801c-a8ec5c214bf8	Kunde11	\N	\N	\N	\N	2026-11-15 20:37:37.595788+01	2026-11-15 20:37:37.595788+01
\.


--
-- Data for Name: daily_summaries; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.daily_summaries (id, user_id, work_date, total_work_minutes, total_break_minutes, is_approved, approved_by, created_at) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.projects (id, company_id, client_id, name, description, is_active, created_at, updated_at) FROM stdin;
f508534f-f712-49e9-a166-e1599481a82e	03118c02-f589-49fb-a4ea-f86a867a72b6	4da054bc-9ac3-4aee-8740-d9e82d514e1f	Test N1 p2	\N	t	2026-10-30 14:13:45.953063+01	2026-10-30 14:13:45.953063+01
31df4626-ff47-4caa-aeb6-3540f4d4745c	03118c02-f589-49fb-a4ea-f86a867a72b6	4da054bc-9ac3-4aee-8740-d9e82d514e1f	Project One S3	Change Project name	f	2026-10-29 16:41:51.586167+01	2026-10-29 16:41:51.586167+01
8fd77110-23d6-4a55-861c-dbbf2643fbab	03118c02-f589-49fb-a4ea-f86a867a72b6	4da054bc-9ac3-4aee-8740-d9e82d514e1f	Test N1 p1	\N	f	2026-10-29 18:23:37.390927+01	2026-10-29 18:23:37.390927+01
\.


--
-- Data for Name: time_entries; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.time_entries (id, user_id, project_id, project_name, client_name, start_time, end_time, duration, created_at, is_manual, approval_status, note, synced_at) FROM stdin;
1eb75e9d-67cb-4c54-93d3-67f0f03c432b	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1		1793366076263	1793369676263	60	2026-10-30 14:30:05.804319+01	t	approved	\N	2026-11-02 15:13:23.168841+01
b3a094e7-08bc-4746-aeb6-63122b781fd6	48333ba1-531b-4936-8727-a7fc0e2e9b3a	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2		1793373276000	1793380476000	120	2026-10-30 14:31:19.873359+01	t	approved	\N	2026-11-02 15:13:23.168841+01
ed2dff4f-67f8-482c-84b4-6a2a14689ab7	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1		1793430165000	1793462205000	534	2026-10-30 15:57:27.004602+01	t	approved	\N	2026-11-02 15:13:23.168841+01
06068ced-c6af-478f-bdda-9b53a92f0441	\N	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Company	1793374835242	1793374969149	2	2026-10-30 16:42:49.182354+01	\N	approved	\N	2026-11-02 15:13:23.168841+01
80ba1fd7-081f-4612-a79c-72fb53229768	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1		1793516623000	1793549083000	541	2026-10-30 16:04:41.281596+01	t	approved	\N	2026-11-02 15:13:23.168841+01
c34526a5-eb97-4b6d-9535-cb3b43e39a61	48333ba1-531b-4936-8727-a7fc0e2e9b3a	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2		1793176431000	1793205231000	480	2026-10-30 16:34:11.185442+01	t	approved	\N	2026-11-02 15:13:23.168841+01
532df78b-6599-4cff-a457-f9f839aa85c0	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1		1793517147000	1793549547778	540	2026-11-01 16:12:58.022786+01	t	approved	\N	2026-11-02 15:13:23.168841+01
0e6aa6fe-f69b-478f-89e9-9575bf82a411	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Hhfgg	1793605123000	1793637523000	540	2026-11-02 13:39:38.333203+01	t	approved	\N	2026-11-02 15:13:23.168841+01
53607822-86df-45ec-83ff-2b8c5bd162da	48333ba1-531b-4936-8727-a7fc0e2e9b3a	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Hhfgg	1793691523000	1793723923000	540	2026-11-02 13:45:13.752678+01	t	approved	\N	2026-11-02 15:13:23.168841+01
9574dfee-6d53-4882-ae15-ba276cc70fb1	48333ba1-531b-4936-8727-a7fc0e2e9b3a	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Hhfgg	1793775766000	1793808166000	540	2026-11-02 14:03:30.789128+01	t	approved	\N	2026-11-02 15:13:23.168841+01
1eb9b313-c43e-4724-ac5c-13cb2ca8b353	\N	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793289621950	1793289682390	1	2026-10-29 17:01:22.375379+01	\N	approved	\N	2026-11-02 15:13:23.168841+01
08025184-7619-43cd-b1e8-927f1cd0f4a3	\N	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793369249300	1793369255565	1	2026-10-30 15:08:10.507752+01	\N	approved	\N	2026-11-02 15:13:23.168841+01
c214c25f-a28e-4796-909e-fcce8541db2c	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793632770261	1793633286194	1	2026-11-02 16:28:06.107062+01	\N	approved		2026-11-02 16:28:06.107062+01
b2ee0f91-1c50-4015-94d1-fabf92f59930	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793631753748	1793632767329	17	2026-11-02 16:19:27.258375+01	\N	approved		2026-11-02 16:19:27.258375+01
a2a91469-cda4-4037-9ca3-c047fbd0d720	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793630750784	1793631751078	17	2026-11-02 16:02:31.171623+01	\N	approved		2026-11-02 16:02:31.171623+01
ea49e795-345b-4f9b-bc78-80c3d386fe37	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793629210432	1793629331426	2	2026-11-02 15:22:39.779827+01	\N	approved		2026-11-02 15:22:39.779827+01
1c7d5b18-3962-4183-90cd-2f70bd025ce3	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793625824931	1793625888381	1	2026-11-02 15:18:44.839034+01	\N	approved		2026-11-02 15:18:44.839034+01
c1f35144-efde-450c-8782-b7160c9b13da	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793625382038	1793625591246	3	2026-11-02 15:18:44.839034+01	\N	approved		2026-11-02 15:18:44.839034+01
226b0b07-8b99-4b06-a724-8059dcce0897	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Hhfgg	1793602848000	1793637588740	529	2026-11-02 16:50:50.616811+01	t	approved	\N	2026-11-02 16:50:50.616811+01
3e8c7a14-1d73-4b65-9f9a-ba879e298dbc	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S2	Company	1793637935556	1793638538919	10	2026-11-02 17:55:38.82486+01	\N	approved		2026-11-02 17:55:38.82486+01
fc7d38aa-6276-4ebf-90b2-7c4e7d76aae0	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Hhfgg	1793652522754	1793656122754	60	2026-11-02 21:48:51.997625+01	t	approved	\N	2026-11-02 21:48:51.997625+01
e9264506-2164-4c6a-bdf6-072c369d6523	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Hhfgg	1793652522754	1793656122754	60	2026-11-02 21:53:31.221855+01	t	pending	\N	2026-11-02 21:53:31.221855+01
b340c499-78f8-4432-ab96-d6b8dbb464dc	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Hhfgg	1793652522754	1793656122754	60	2026-11-02 22:24:18.789251+01	t	pending	\N	2026-11-02 22:24:18.789251+01
1974a111-f3b0-464c-bc69-9a5342304138	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Hhfgg	1793652522754	1793656122754	60	2026-11-02 22:31:26.105939+01	t	pending	\N	2026-11-02 22:31:26.105939+01
3247eb28-4949-44fa-a2fd-c6b090e3e447	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Hhfgg	1793652522754	1793656122754	60	2026-11-02 22:32:17.315277+01	t	pending	\N	2026-11-02 22:32:17.315277+01
a00819ab-75ca-43de-8083-d60617c00649	70748830-4d99-4a4f-a015-f76d4f27720e	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Hhfgg	1793655610422	1793659210422	60	2026-11-02 22:40:28.528319+01	t	approved	\N	2026-11-02 22:40:28.528319+01
262e9865-bf0f-4735-9f1f-0b1b151aacf3	4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Hhfgg	1793655610422	1793659210422	60	2026-11-02 22:41:00.330006+01	t	approved	\N	2026-11-02 22:41:00.330006+01
91be7418-8357-421d-b12b-5b76d2d0298b	0ab9edff-aa40-48f8-915d-068a164e59e8	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Hhfgg	1793655610422	1793659210422	60	2026-11-02 22:41:23.348364+01	t	approved	\N	2026-11-02 22:41:23.348364+01
c97d010e-6631-4c67-a8e1-be8af54abb62	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1793649605032	1793697227575	794	2026-11-03 10:13:47.685885+01	\N	pending		2026-11-03 10:13:47.685885+01
faa0670a-e0a1-46be-a353-7a27e5bc3cbc	4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Hhfgg	1793655610422	1793659210422	60	2026-11-03 10:16:52.540849+01	t	approved	\N	2026-11-03 10:16:52.540849+01
6515bc9c-6b70-4665-81fd-da52d5eaa650	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1793709327414	1793711022023	11	2026-11-03 14:03:41.88862+01	\N	pending		2026-11-03 14:03:41.88862+01
71366968-a33c-422b-9825-adc065a8e983	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1793720516863	1793720522140	1	2026-11-03 16:42:02.120766+01	\N	pending		2026-11-03 16:42:02.120766+01
7f0a4bba-954b-4de5-b826-14a9645a5114	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1793723525358	1793734992683	191	2026-11-03 22:01:06.868202+01	\N	pending		2026-11-03 22:01:06.868202+01
15668344-d701-420a-929c-b91581a0e30a	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Company	1794138683001	1794139382537	12	2026-11-08 13:03:04.809869+01	\N	pending		2026-11-08 13:03:04.809869+01
2adb4f00-fd1d-4649-a30e-5126a42cbc25	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Company	1794211661498	1794398519676	3114	2026-11-11 13:01:59.820511+01	\N	pending		2026-11-11 13:01:59.820511+01
52f527c7-615f-4f84-8b74-cb8e36d773fb	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Company	1794168643312	1794180346086	195	2026-11-11 13:01:59.820511+01	\N	pending		2026-11-11 13:01:59.820511+01
9bad099f-af23-4f9b-9650-7db2b2f35514	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1794138638888	1794138675315	1	2026-11-08 12:51:17.642579+01	\N	approved		2026-11-08 12:51:17.642579+01
c2e8f965-23b7-4723-b83e-a740246fb9b6	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1794648092297	1794648155314	1	2026-11-14 10:22:36.050961+01	\N	pending		2026-11-14 10:22:36.050961+01
33b490a4-7cb4-48b7-a4d2-610d99c27c85	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1794653196566	1794653260195	1	2026-11-14 11:47:40.351775+01	\N	pending		2026-11-14 11:47:40.351775+01
3d6d3cf2-31fc-4190-9e39-bc54d90b0dda	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	taghiir	1793742378308	1793806891998	50	2026-11-04 16:41:32.069035+01	\N	approved		2026-11-04 16:41:32.069035+01
8de1ef23-eab4-4cba-aa7a-3462cc28ed1e	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Hhfgg	1794648838376	1794652600428	61	2026-11-14 11:36:40.628299+01	\N	approved		2026-11-14 11:36:40.628299+01
0812073e-44b4-403c-b53d-9bd2654fb4cd	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Company	1794744686284	1794744776303	2	2026-11-15 13:12:55.912104+01	\N	pending		2026-11-15 13:12:55.912104+01
766c5b0c-4bf6-4f00-9f7c-faab6679cd83	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Company	1794744913160	1794745778021	14	2026-11-15 13:29:37.627514+01	\N	pending		2026-11-15 13:29:37.627514+01
244c0e75-089d-48f0-89a7-e18fa5a6dcaf	48333ba1-531b-4936-8727-a7fc0e2e9b3a	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Company	1794746006277	1794746013195	1	2026-11-15 13:33:32.791063+01	\N	pending		2026-11-15 13:33:32.791063+01
e057d25e-329b-4df5-844c-c4bb4e82f553	48333ba1-531b-4936-8727-a7fc0e2e9b3a	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Hhfgg	1794750771326	1794754371326	60	2026-11-15 14:54:31.139156+01	t	approved	\N	2026-11-15 14:54:31.139156+01
99afc174-0074-4d72-a60c-bc143a2dcd40	0ab9edff-aa40-48f8-915d-068a164e59e8	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Hhfgg	1794750771326	1794754371326	60	2026-11-15 14:55:35.271782+01	t	approved	\N	2026-11-15 14:55:35.271782+01
594d5f5d-782b-4f3a-a4df-9505f7967069	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	f508534f-f712-49e9-a166-e1599481a82e	Test N1 p2	Hhfgg	1789496871000	1789507671000	180	2026-11-15 20:29:52.315211+01	t	pending	\N	2026-11-15 20:29:52.315211+01
1ea99cf0-d4e6-48bd-ba6b-61b1539e02cf	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	Project One S3	Company	1794771389975	1794771395670	1	2026-11-15 20:36:35.398446+01	\N	pending		2026-11-15 20:36:35.398446+01
20b065fd-4f56-415a-9bb4-e0df2e7e90a0	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	8fd77110-23d6-4a55-861c-dbbf2643fbab	Test N1 p1	Company	1794771402271	1794771407056	1	2026-11-15 20:36:46.774188+01	\N	pending		2026-11-15 20:36:46.774188+01
\.


--
-- Data for Name: user_projects; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects (id, user_id, project_id, created_at) FROM stdin;
1	70748830-4d99-4a4f-a015-f76d4f27720e	31df4626-ff47-4caa-aeb6-3540f4d4745c	2026-10-29 17:35:39.84671
2	4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	31df4626-ff47-4caa-aeb6-3540f4d4745c	2026-10-29 18:02:01.479646
3	48333ba1-531b-4936-8727-a7fc0e2e9b3a	8fd77110-23d6-4a55-861c-dbbf2643fbab	2026-10-29 18:23:50.696098
4	48333ba1-531b-4936-8727-a7fc0e2e9b3a	f508534f-f712-49e9-a166-e1599481a82e	2026-10-30 14:13:56.304721
5	0ab9edff-aa40-48f8-915d-068a164e59e8	31df4626-ff47-4caa-aeb6-3540f4d4745c	2026-10-30 15:10:15.883202
6	0ab9edff-aa40-48f8-915d-068a164e59e8	f508534f-f712-49e9-a166-e1599481a82e	2026-10-30 15:10:16.644618
7	6d6c29f6-03e6-424a-8d92-1a62657b12df	31df4626-ff47-4caa-aeb6-3540f4d4745c	2026-11-02 14:10:18.60036
10	9f32025c-4769-4bbb-8519-abede42cfc9d	31df4626-ff47-4caa-aeb6-3540f4d4745c	2026-11-02 14:11:34.171685
11	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	31df4626-ff47-4caa-aeb6-3540f4d4745c	2026-11-14 13:35:38.103329
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

COPY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.users (id, email, full_name, role, is_active, created_at, password_hash, include_in_reports) FROM stdin;
70748830-4d99-4a4f-a015-f76d4f27720e	ghg	Ggf	admin	t	2026-10-29 16:40:05.645852+01	\N	t
6d6c29f6-03e6-424a-8d92-1a62657b12df	\N	Test bee	employee	t	2026-10-29 18:01:10.855845+01	\N	t
4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	\N	Test normal	employee	t	2026-10-29 18:01:52.167025+01	\N	t
c15278b4-2c5e-4ec7-a0d2-0d38be078aab	amir@yahoo.com	Test addd	admin	t	2026-10-29 18:01:20.147429+01	$2b$12$ULo0a.bHKmSyJzkw9AN04Ovy.tA62SejHzDCMNW6mhsBEXZCozXba	t
241da9c6-d917-4abd-ad20-7994b10ee5d4	\N	Raheleh	employee	t	2026-10-30 15:09:01.65121+01	\N	t
de2f94d1-0189-4678-8992-f5a98028561e	\N	Raheleh	employee	t	2026-10-30 15:09:02.208704+01	\N	t
5739db7e-b49e-4153-9a8d-d6ecad8a6516	\N	Ttt	employee	t	2026-10-29 18:01:00.23973+01	\N	f
0ab9edff-aa40-48f8-915d-068a164e59e8	\N	Raheleh	employee	t	2026-10-30 15:09:06.89692+01	\N	t
9f32025c-4769-4bbb-8519-abede42cfc9d	\N	Frank	employee	t	2026-11-02 14:10:54.383519+01	\N	t
98cd137c-ac87-4d7c-a380-b159cb9c1396	\N	Hfgkjg	employee	t	2026-11-08 12:52:43.569005+01	\N	t
48333ba1-531b-4936-8727-a7fc0e2e9b3a	amir_amarloo@yahoo.com	N1	employee	t	2026-10-29 18:20:59.898989+01	$2b$12$GXKEUmXzVpjnkYLrObKA4.XExn3S7k1wMFQcjhcxhHkdMH2fblIp6	t
e3309fe3-3e90-4967-9777-4b5a65e6fef1	\N	Hodaa	employee	t	2026-11-15 20:35:15.715432+01	\N	t
\.


--
-- Data for Name: activation_tokens; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.activation_tokens (id, company_user_id, token, expires_at, used_at, created_at, updated_at) FROM stdin;
392cc26d-812d-4ee0-adac-0e20d8f9f2c3	e82d7271-2f0f-41f0-a497-8990c5f3fb67	EMP_TOKEN_d6dbcc2a	2026-11-05 16:21:35.257651+01	\N	2026-10-29 16:21:35.257651+01	\N
ce3ea4de-9d57-42ef-8163-9dc14c3aa456	18306933-2b39-4de1-8acb-c22dfbd23085	EMP_TOKEN_61e876f8	2026-11-05 16:22:37.809135+01	\N	2026-10-29 16:22:37.809135+01	\N
18c11287-2510-4191-8908-7d3ce5da4ab5	6ca9c615-f5cf-4c8f-bba5-93cf9f14f8dc	EMP_TOKEN_90e42472	2026-11-05 16:27:17.16361+01	\N	2026-10-29 16:27:17.16361+01	\N
49f12540-c3e0-4a57-9e60-fd3859af1e99	b3c7fb9d-20e9-4f74-b50a-81c0a10cf583	EMP_TOKEN_64b8d98b	2026-11-05 16:28:27.511774+01	\N	2026-10-29 16:28:27.511774+01	\N
c233d7d3-571d-4e19-a04d-32a8df226330	5af33af5-547c-4732-8ff8-2801b930756f	EMP_TOKEN_7374a6b3	2026-11-05 16:30:03.158501+01	\N	2026-10-29 16:30:03.158501+01	\N
d355a46f-51a8-4caa-8681-704799aadb00	53ff0707-3f1b-4d6d-89f3-37d6d45ec341	EMP_TOKEN_a20ba674	2026-11-05 16:40:12.870567+01	\N	2026-10-29 16:40:12.870567+01	\N
513e2b9e-2ada-4d54-a05e-4b8ea142329a	b54d9607-b255-4c6b-b710-5bb88e51bd5c	EMP_TOKEN_5b1d16df	2026-11-05 16:42:40.893732+01	\N	2026-10-29 16:42:40.893732+01	\N
e632570e-93ad-4fc4-ab78-cc9f9afd711d	fbd6d564-97b4-4960-bf10-1dde6681bd6d	EMP_TOKEN_f003e4b8	2026-11-05 17:23:43.040359+01	\N	2026-10-29 17:23:43.040359+01	\N
09475630-d8e7-4d47-8ccf-eaf4475100a0	45cd2161-1815-4b6a-aa7f-ebcc47196d88	EMP_TOKEN_f0c8930b	2026-11-05 17:26:09.148257+01	\N	2026-10-29 17:26:09.148257+01	\N
af7da278-0c39-414f-bca6-88adce1d1ec2	5739db7e-b49e-4153-9a8d-d6ecad8a6516	EMP_TOKEN_2c916340	2026-11-05 18:01:00.23973+01	\N	2026-10-29 18:01:00.23973+01	\N
1d1a49ff-1ac0-46c7-8c4c-7bced624a3c5	6d6c29f6-03e6-424a-8d92-1a62657b12df	EMP_TOKEN_07abec81	2026-11-05 18:01:10.855845+01	\N	2026-10-29 18:01:10.855845+01	\N
60cf98fa-4a21-4a82-a451-b57a02b998be	4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	EMP_TOKEN_89f35a22	2026-11-05 18:01:52.167025+01	\N	2026-10-29 18:01:52.167025+01	\N
c94ea07f-e54f-4e9d-9ab7-87085f6bcd62	48333ba1-531b-4936-8727-a7fc0e2e9b3a	EMP_TOKEN_b34e8c3d	2026-11-05 18:20:59.898989+01	2026-10-30 13:26:40.268071+01	2026-10-29 18:20:59.898989+01	13:26:40.268071+01
bb3f8cd2-8fdf-4f7d-9a15-a333f2ce21e5	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	EMP_TOKEN_e4b3894c	2026-11-05 18:01:20.147429+01	2026-10-30 13:54:49.414897+01	2026-10-29 18:01:20.147429+01	13:54:49.414897+01
65d7f218-8bc6-43e4-b4fa-13a08c742ddf	241da9c6-d917-4abd-ad20-7994b10ee5d4	EMP_TOKEN_0172e4ab	2026-11-06 15:09:01.65121+01	\N	2026-10-30 15:09:01.65121+01	\N
f9222a1a-d2b7-4ed9-967d-1ba68d778ddd	de2f94d1-0189-4678-8992-f5a98028561e	EMP_TOKEN_36fc98ae	2026-11-06 15:09:02.208704+01	\N	2026-10-30 15:09:02.208704+01	\N
da5fcee3-4c99-4c58-98b3-3f3862a09975	0ab9edff-aa40-48f8-915d-068a164e59e8	EMP_TOKEN_9093a0db	2026-11-06 15:09:06.89692+01	\N	2026-10-30 15:09:06.89692+01	\N
b382d234-7e57-403a-a6d9-8a0753f1d63b	9f32025c-4769-4bbb-8519-abede42cfc9d	EMP_TOKEN_5b25d3dd	2026-11-09 14:10:54.383519+01	\N	2026-11-02 14:10:54.383519+01	\N
08cb3ccd-c3e3-4a4e-90f7-d0fa4cb0be27	98cd137c-ac87-4d7c-a380-b159cb9c1396	EMP_TOKEN_afd69907	2026-11-15 12:52:43.569005+01	\N	2026-11-08 12:52:43.569005+01	\N
5795f5e5-5c3f-4fb1-8b68-f3cb68ebdce1	e3309fe3-3e90-4967-9777-4b5a65e6fef1	EMP_TOKEN_1051b7b8	2026-11-22 20:35:15.715432+01	\N	2026-11-15 20:35:15.715432+01	\N
\.
*/

--
-- Data for Name: active_sessions; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.active_sessions (id, company_id, project_id, company_user_id, start_time, is_manual, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: clients; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.clients (id, company_id, name, address, contact_name, contact_email, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.companies (id, name, address, created_at, updated_at) FROM stdin;
fffa3af0-59bb-4ed2-93cb-563b4d0d14b4	Test Fresh Co	\N	2026-10-29 15:57:57.377824+01	2026-10-29 15:57:57.377824+01
5016a041-2f89-4ac8-82bf-778ca45dda35	Test Co	\N	2026-10-29 16:19:05.632338+01	2026-10-29 16:19:05.632338+01
1cf8d707-41b4-4c72-9c39-61d8cdb2b427	Ttt	\N	2026-10-29 16:28:14.916236+01	2026-10-29 16:28:14.916236+01
1d4afac3-2b13-4e52-a26d-220f8a05d1fb	Hh	\N	2026-10-29 16:29:54.76284+01	2026-10-29 16:29:54.76284+01
03118c02-f589-49fb-a4ea-f86a867a72b6	Hgf	\N	2026-10-29 16:40:05.595281+01	2026-10-29 16:40:05.595281+01
\.


--
-- Data for Name: company_users; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.company_users (id, company_id, user_id, status, created_at, updated_at, role) FROM stdin;
1743fff1-9a55-42bf-be84-fda4e91d044e	fffa3af0-59bb-4ed2-93cb-563b4d0d14b4	1743fff1-9a55-42bf-be84-fda4e91d044e	active	2026-10-29 15:57:57.377824+01	2026-10-29 15:57:57.377824+01	admin
5ff06811-abce-427f-beac-95f44aaa21c3	5016a041-2f89-4ac8-82bf-778ca45dda35	5ff06811-abce-427f-beac-95f44aaa21c3	active	2026-10-29 16:19:05.632338+01	2026-10-29 16:19:05.632338+01	admin
e82d7271-2f0f-41f0-a497-8990c5f3fb67	5016a041-2f89-4ac8-82bf-778ca45dda35	e82d7271-2f0f-41f0-a497-8990c5f3fb67	active	2026-10-29 16:21:35.257651+01	2026-10-29 16:21:35.257651+01	employee
18306933-2b39-4de1-8acb-c22dfbd23085	5016a041-2f89-4ac8-82bf-778ca45dda35	18306933-2b39-4de1-8acb-c22dfbd23085	active	2026-10-29 16:22:37.809135+01	2026-10-29 16:22:37.809135+01	employee
6ca9c615-f5cf-4c8f-bba5-93cf9f14f8dc	5016a041-2f89-4ac8-82bf-778ca45dda35	6ca9c615-f5cf-4c8f-bba5-93cf9f14f8dc	active	2026-10-29 16:27:17.16361+01	2026-10-29 16:27:17.16361+01	employee
e768a616-e9ea-4534-8167-f65d813e92c7	1cf8d707-41b4-4c72-9c39-61d8cdb2b427	e768a616-e9ea-4534-8167-f65d813e92c7	active	2026-10-29 16:28:14.916236+01	2026-10-29 16:28:14.916236+01	admin
b3c7fb9d-20e9-4f74-b50a-81c0a10cf583	1cf8d707-41b4-4c72-9c39-61d8cdb2b427	b3c7fb9d-20e9-4f74-b50a-81c0a10cf583	active	2026-10-29 16:28:27.511774+01	2026-10-29 16:28:27.511774+01	employee
cd5bdaf1-20d6-4703-9d8e-8558710b6c09	1d4afac3-2b13-4e52-a26d-220f8a05d1fb	cd5bdaf1-20d6-4703-9d8e-8558710b6c09	active	2026-10-29 16:29:54.76284+01	2026-10-29 16:29:54.76284+01	admin
5af33af5-547c-4732-8ff8-2801b930756f	1d4afac3-2b13-4e52-a26d-220f8a05d1fb	5af33af5-547c-4732-8ff8-2801b930756f	active	2026-10-29 16:30:03.158501+01	2026-10-29 16:30:03.158501+01	employee
70748830-4d99-4a4f-a015-f76d4f27720e	03118c02-f589-49fb-a4ea-f86a867a72b6	70748830-4d99-4a4f-a015-f76d4f27720e	active	2026-10-29 16:40:05.595281+01	2026-10-29 16:40:05.595281+01	admin
53ff0707-3f1b-4d6d-89f3-37d6d45ec341	03118c02-f589-49fb-a4ea-f86a867a72b6	53ff0707-3f1b-4d6d-89f3-37d6d45ec341	active	2026-10-29 16:40:12.870567+01	2026-10-29 16:40:12.870567+01	employee
b54d9607-b255-4c6b-b710-5bb88e51bd5c	03118c02-f589-49fb-a4ea-f86a867a72b6	b54d9607-b255-4c6b-b710-5bb88e51bd5c	active	2026-10-29 16:42:40.893732+01	2026-10-29 16:42:40.893732+01	employee
fbd6d564-97b4-4960-bf10-1dde6681bd6d	03118c02-f589-49fb-a4ea-f86a867a72b6	fbd6d564-97b4-4960-bf10-1dde6681bd6d	active	2026-10-29 17:23:43.040359+01	2026-10-29 17:23:43.040359+01	employee
45cd2161-1815-4b6a-aa7f-ebcc47196d88	03118c02-f589-49fb-a4ea-f86a867a72b6	45cd2161-1815-4b6a-aa7f-ebcc47196d88	active	2026-10-29 17:26:09.148257+01	2026-10-29 17:26:09.148257+01	admin
5739db7e-b49e-4153-9a8d-d6ecad8a6516	03118c02-f589-49fb-a4ea-f86a867a72b6	5739db7e-b49e-4153-9a8d-d6ecad8a6516	active	2026-10-29 18:01:00.23973+01	2026-10-29 18:01:00.23973+01	employee
6d6c29f6-03e6-424a-8d92-1a62657b12df	03118c02-f589-49fb-a4ea-f86a867a72b6	6d6c29f6-03e6-424a-8d92-1a62657b12df	active	2026-10-29 18:01:10.855845+01	2026-10-29 18:01:10.855845+01	employee
c15278b4-2c5e-4ec7-a0d2-0d38be078aab	03118c02-f589-49fb-a4ea-f86a867a72b6	c15278b4-2c5e-4ec7-a0d2-0d38be078aab	active	2026-10-29 18:01:20.147429+01	2026-10-29 18:01:20.147429+01	admin
4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	03118c02-f589-49fb-a4ea-f86a867a72b6	4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	active	2026-10-29 18:01:52.167025+01	2026-10-29 18:01:52.167025+01	employee
48333ba1-531b-4936-8727-a7fc0e2e9b3a	03118c02-f589-49fb-a4ea-f86a867a72b6	48333ba1-531b-4936-8727-a7fc0e2e9b3a	active	2026-10-29 18:20:59.898989+01	2026-10-29 18:20:59.898989+01	employee
241da9c6-d917-4abd-ad20-7994b10ee5d4	03118c02-f589-49fb-a4ea-f86a867a72b6	241da9c6-d917-4abd-ad20-7994b10ee5d4	active	2026-10-30 15:09:01.65121+01	2026-10-30 15:09:01.65121+01	employee
de2f94d1-0189-4678-8992-f5a98028561e	03118c02-f589-49fb-a4ea-f86a867a72b6	de2f94d1-0189-4678-8992-f5a98028561e	active	2026-10-30 15:09:02.208704+01	2026-10-30 15:09:02.208704+01	employee
0ab9edff-aa40-48f8-915d-068a164e59e8	03118c02-f589-49fb-a4ea-f86a867a72b6	0ab9edff-aa40-48f8-915d-068a164e59e8	active	2026-10-30 15:09:06.89692+01	2026-10-30 15:09:06.89692+01	employee
9f32025c-4769-4bbb-8519-abede42cfc9d	03118c02-f589-49fb-a4ea-f86a867a72b6	9f32025c-4769-4bbb-8519-abede42cfc9d	active	2026-11-02 14:10:54.383519+01	2026-11-02 14:10:54.383519+01	employee
98cd137c-ac87-4d7c-a380-b159cb9c1396	03118c02-f589-49fb-a4ea-f86a867a72b6	98cd137c-ac87-4d7c-a380-b159cb9c1396	active	2026-11-08 12:52:43.569005+01	2026-11-08 12:52:43.569005+01	employee
e3309fe3-3e90-4967-9777-4b5a65e6fef1	03118c02-f589-49fb-a4ea-f86a867a72b6	e3309fe3-3e90-4967-9777-4b5a65e6fef1	active	2026-11-15 20:35:15.715432+01	2026-11-15 20:35:15.715432+01	employee
\.


--
-- Data for Name: project_assignments; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.project_assignments (id, project_id, company_user_id, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.projects (id, company_id, name, description, is_active, created_at, updated_at, client_id) FROM stdin;
\.


--
-- Data for Name: time_entries; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.time_entries (id, company_id, project_id, company_user_id, start_time, end_time, duration_minutes, status, is_manual, is_over_limit, justification_note, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: timetracker; Owner: postgres
--

COPY timetracker.users (id, email, display_name, role, created_at, updated_at, password_hash, is_active) FROM stdin;
1743fff1-9a55-42bf-be84-fda4e91d044e	\N	Aworker	admin	2026-10-29 15:57:57.377824+01	2026-10-29 15:57:57.377824+01	\N	t
5ff06811-abce-427f-beac-95f44aaa21c3	\N	Ad1	admin	2026-10-29 16:19:05.632338+01	2026-10-29 16:19:05.632338+01	\N	t
e82d7271-2f0f-41f0-a497-8990c5f3fb67	\N	AmirHooshang normal	employee	2026-10-29 16:21:35.257651+01	2026-10-29 16:21:35.257651+01	\N	t
18306933-2b39-4de1-8acb-c22dfbd23085	\N	Test user normal	employee	2026-10-29 16:22:37.809135+01	2026-10-29 16:22:37.809135+01	\N	t
6ca9c615-f5cf-4c8f-bba5-93cf9f14f8dc	\N	Test normal2	employee	2026-10-29 16:27:17.16361+01	2026-10-29 16:27:17.16361+01	\N	t
e768a616-e9ea-4534-8167-f65d813e92c7	\N	Fff	admin	2026-10-29 16:28:14.916236+01	2026-10-29 16:28:14.916236+01	\N	t
b3c7fb9d-20e9-4f74-b50a-81c0a10cf583	\N	Fgggg	employee	2026-10-29 16:28:27.511774+01	2026-10-29 16:28:27.511774+01	\N	t
cd5bdaf1-20d6-4703-9d8e-8558710b6c09	\N	Vv	admin	2026-10-29 16:29:54.76284+01	2026-10-29 16:29:54.76284+01	\N	t
5af33af5-547c-4732-8ff8-2801b930756f	\N	Hhfgj	employee	2026-10-29 16:30:03.158501+01	2026-10-29 16:30:03.158501+01	\N	t
70748830-4d99-4a4f-a015-f76d4f27720e	\N	Ggf	admin	2026-10-29 16:40:05.595281+01	2026-10-29 16:40:05.595281+01	\N	t
53ff0707-3f1b-4d6d-89f3-37d6d45ec341	\N	Hfdhj	employee	2026-10-29 16:40:12.870567+01	2026-10-29 16:40:12.870567+01	\N	t
b54d9607-b255-4c6b-b710-5bb88e51bd5c	\N	Gxgjnvv	employee	2026-10-29 16:42:40.893732+01	2026-10-29 16:42:40.893732+01	\N	t
fbd6d564-97b4-4960-bf10-1dde6681bd6d	\N	Test admin	employee	2026-10-29 17:23:43.040359+01	2026-10-29 17:23:43.040359+01	\N	t
45cd2161-1815-4b6a-aa7f-ebcc47196d88	\N	Test add add	admin	2026-10-29 17:26:09.148257+01	2026-10-29 17:26:09.148257+01	\N	t
5739db7e-b49e-4153-9a8d-d6ecad8a6516	\N	Ttt	employee	2026-10-29 18:01:00.23973+01	2026-10-29 18:01:00.23973+01	\N	t
6d6c29f6-03e6-424a-8d92-1a62657b12df	\N	Test bee	employee	2026-10-29 18:01:10.855845+01	2026-10-29 18:01:10.855845+01	\N	t
4b4494e7-b2a9-4d18-9e1f-c8c319e1191a	\N	Test normal	employee	2026-10-29 18:01:52.167025+01	2026-10-29 18:01:52.167025+01	\N	t
c15278b4-2c5e-4ec7-a0d2-0d38be078aab	amir@yahoo.com	Test addd	admin	2026-10-29 18:01:20.147429+01	2026-10-30 13:54:49.414897+01	$2b$12$ULo0a.bHKmSyJzkw9AN04Ovy.tA62SejHzDCMNW6mhsBEXZCozXba	t
241da9c6-d917-4abd-ad20-7994b10ee5d4	\N	Raheleh	employee	2026-10-30 15:09:01.65121+01	2026-10-30 15:09:01.65121+01	\N	t
de2f94d1-0189-4678-8992-f5a98028561e	\N	Raheleh	employee	2026-10-30 15:09:02.208704+01	2026-10-30 15:09:02.208704+01	\N	t
0ab9edff-aa40-48f8-915d-068a164e59e8	\N	Raheleh	employee	2026-10-30 15:09:06.89692+01	2026-10-30 15:09:06.89692+01	\N	t
9f32025c-4769-4bbb-8519-abede42cfc9d	\N	Frank	employee	2026-11-02 14:10:54.383519+01	2026-11-02 14:10:54.383519+01	\N	t
98cd137c-ac87-4d7c-a380-b159cb9c1396	\N	Hfgkjg	employee	2026-11-08 12:52:43.569005+01	2026-11-08 12:52:43.569005+01	\N	t
48333ba1-531b-4936-8727-a7fc0e2e9b3a	amir_amarloo@yahoo.com	N1	employee	2026-10-29 18:20:59.898989+01	2026-11-15 14:49:08.243534+01	$2b$12$GXKEUmXzVpjnkYLrObKA4.XExn3S7k1wMFQcjhcxhHkdMH2fblIp6	f
e3309fe3-3e90-4967-9777-4b5a65e6fef1	\N	Hodaa	employee	2026-11-15 20:35:15.715432+01	2026-11-15 20:35:15.715432+01	\N	t
\.


--
-- Name: user_projects_id_seq; Type: SEQUENCE SET; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

--SELECT pg_catalog.setval('tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects_id_seq', 11, true);


--
-- Name: timetrackercompanies timetrackercompanies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timetrackercompanies
    ADD CONSTRAINT timetrackercompanies_pkey PRIMARY KEY (id);


--
-- Name: absences absences_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--
/*
ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.absences
    ADD CONSTRAINT absences_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: breaks breaks_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.breaks
    ADD CONSTRAINT breaks_pkey PRIMARY KEY (id);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: daily_summaries daily_summaries_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.daily_summaries
    ADD CONSTRAINT daily_summaries_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: time_entries time_entries_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.time_entries
    ADD CONSTRAINT time_entries_pkey PRIMARY KEY (id);


--
-- Name: daily_summaries unique_user_date_tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.daily_summaries
    ADD CONSTRAINT unique_user_date_tenant_03118c02_f589_49fb_a4ea_f86a867a72b6 UNIQUE (user_id, work_date);


--
-- Name: user_projects user_projects_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects
    ADD CONSTRAINT user_projects_pkey PRIMARY KEY (id);


--
-- Name: user_projects user_projects_user_id_project_id_key; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.user_projects
    ADD CONSTRAINT user_projects_user_id_project_id_key UNIQUE (user_id, project_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

*/
--
-- Name: activation_tokens activation_tokens_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.activation_tokens
    ADD CONSTRAINT activation_tokens_pkey PRIMARY KEY (id);


--
-- Name: activation_tokens activation_tokens_token_key; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.activation_tokens
    ADD CONSTRAINT activation_tokens_token_key UNIQUE (token);


--
-- Name: active_sessions active_sessions_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.active_sessions
    ADD CONSTRAINT active_sessions_pkey PRIMARY KEY (id);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: company_users company_users_company_id_user_id_key; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.company_users
    ADD CONSTRAINT company_users_company_id_user_id_key UNIQUE (company_id, user_id);


--
-- Name: company_users company_users_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.company_users
    ADD CONSTRAINT company_users_pkey PRIMARY KEY (id);


--
-- Name: project_assignments project_assignments_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.project_assignments
    ADD CONSTRAINT project_assignments_pkey PRIMARY KEY (id);


--
-- Name: project_assignments project_assignments_project_id_company_user_id_key; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.project_assignments
    ADD CONSTRAINT project_assignments_project_id_company_user_id_key UNIQUE (project_id, company_user_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: time_entries time_entries_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.time_entries
    ADD CONSTRAINT time_entries_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_active_sessions_company; Type: INDEX; Schema: timetracker; Owner: postgres
--

CREATE INDEX idx_active_sessions_company ON timetracker.active_sessions USING btree (company_id);


--
-- Name: idx_time_entries_company_date; Type: INDEX; Schema: timetracker; Owner: postgres
--

CREATE INDEX idx_time_entries_company_date ON timetracker.time_entries USING btree (company_id, start_time);


--
-- Name: activation_tokens update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.activation_tokens FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: clients update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.clients FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: companies update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.companies FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: company_users update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.company_users FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: project_assignments update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.project_assignments FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: projects update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.projects FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: time_entries update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.time_entries FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: users update_timestamp; Type: TRIGGER; Schema: timetracker; Owner: postgres
--

CREATE TRIGGER update_timestamp BEFORE UPDATE ON timetracker.users FOR EACH ROW EXECUTE FUNCTION timetracker.update_timestamp();


--
-- Name: breaks breaks_time_entry_id_fkey; Type: FK CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--
/*
ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.breaks
    ADD CONSTRAINT breaks_time_entry_id_fkey FOREIGN KEY (time_entry_id) REFERENCES tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.time_entries(id) ON DELETE CASCADE;


--
-- Name: projects projects_client_id_fkey; Type: FK CONSTRAINT; Schema: tenant_03118c02_f589_49fb_a4ea_f86a867a72b6; Owner: postgres
--

ALTER TABLE ONLY tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.projects
    ADD CONSTRAINT projects_client_id_fkey FOREIGN KEY (client_id) REFERENCES tenant_03118c02_f589_49fb_a4ea_f86a867a72b6.clients(id) ON DELETE CASCADE;

*/
--
-- Name: activation_tokens activation_tokens_company_user_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.activation_tokens
    ADD CONSTRAINT activation_tokens_company_user_id_fkey FOREIGN KEY (company_user_id) REFERENCES timetracker.company_users(id);


--
-- Name: active_sessions active_sessions_company_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.active_sessions
    ADD CONSTRAINT active_sessions_company_id_fkey FOREIGN KEY (company_id) REFERENCES timetracker.companies(id);


--
-- Name: active_sessions active_sessions_company_user_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.active_sessions
    ADD CONSTRAINT active_sessions_company_user_id_fkey FOREIGN KEY (company_user_id) REFERENCES timetracker.company_users(id);


--
-- Name: active_sessions active_sessions_project_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.active_sessions
    ADD CONSTRAINT active_sessions_project_id_fkey FOREIGN KEY (project_id) REFERENCES timetracker.projects(id);


--
-- Name: clients clients_company_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.clients
    ADD CONSTRAINT clients_company_id_fkey FOREIGN KEY (company_id) REFERENCES timetracker.companies(id);


--
-- Name: company_users company_users_company_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.company_users
    ADD CONSTRAINT company_users_company_id_fkey FOREIGN KEY (company_id) REFERENCES timetracker.companies(id);


--
-- Name: company_users company_users_user_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.company_users
    ADD CONSTRAINT company_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES timetracker.users(id);


--
-- Name: project_assignments project_assignments_company_user_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.project_assignments
    ADD CONSTRAINT project_assignments_company_user_id_fkey FOREIGN KEY (company_user_id) REFERENCES timetracker.company_users(id);


--
-- Name: project_assignments project_assignments_project_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.project_assignments
    ADD CONSTRAINT project_assignments_project_id_fkey FOREIGN KEY (project_id) REFERENCES timetracker.projects(id);


--
-- Name: projects projects_client_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.projects
    ADD CONSTRAINT projects_client_id_fkey FOREIGN KEY (client_id) REFERENCES timetracker.clients(id);


--
-- Name: projects projects_company_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.projects
    ADD CONSTRAINT projects_company_id_fkey FOREIGN KEY (company_id) REFERENCES timetracker.companies(id);


--
-- Name: time_entries time_entries_company_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.time_entries
    ADD CONSTRAINT time_entries_company_id_fkey FOREIGN KEY (company_id) REFERENCES timetracker.companies(id);


--
-- Name: time_entries time_entries_company_user_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.time_entries
    ADD CONSTRAINT time_entries_company_user_id_fkey FOREIGN KEY (company_user_id) REFERENCES timetracker.company_users(id);


--
-- Name: time_entries time_entries_project_id_fkey; Type: FK CONSTRAINT; Schema: timetracker; Owner: postgres
--

ALTER TABLE ONLY timetracker.time_entries
    ADD CONSTRAINT time_entries_project_id_fkey FOREIGN KEY (project_id) REFERENCES timetracker.projects(id);


--
-- PostgreSQL database dump complete
--

\unrestrict j05DURLF8eejtLNwejvhc4oL4XyGtmRFsFKf4yAArlydmy5xV5EMJHt2v9kXo7P

