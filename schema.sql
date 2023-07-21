
CREATE DATABASE nikedb
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'Korean_Korea.949'
       LC_CTYPE = 'Korean_Korea.949'
       CONNECTION LIMIT = -1;

CREATE TABLE tokens (
    id uuid NOT NULL,
    user_id bigint NOT NULL,
    ip_address inet NOT NULL,
    user_agent text,
    created timestamp with time zone DEFAULT now() NOT NULL,
    expired timestamp with time zone DEFAULT (now() + '365 days'::interval) NOT NULL
);


CREATE TABLE sessions (
    id uuid NOT NULL,
    user_id bigint NOT NULL,
    ip_address inet NOT NULL,
    user_agent text,
    ott boolean DEFAULT false,
    created timestamp with time zone DEFAULT now() NOT NULL,
    expired timestamp with time zone DEFAULT (now() + '21 days'::interval) NOT NULL
);


CREATE TABLE users (
    ID bigint NOT NULL,
    USERNAME text NOT NULL,
    PASSWORD text NOT NULL,
    mfa_secret text,
    REG_DATE timestamp with time zone DEFAULT now() NOT NULL,
    LAST_LOGIN_DATE timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE users_id_seq OWNED BY users.ID;

ALTER TABLE ONLY users ALTER COLUMN ID SET DEFAULT nextval('users_id_seq'::regclass);



CREATE VIEW users_view AS
 SELECT u.id,
    u.username,
    u.email,
    u.password,
    u.mfa_secret,
   FROM users u;

CREATE TABLE product (
    ID bigint NOT NULL,
    PRDT_CD text NOT NULL,
    BRAND text NOT NULL,
    TYPE text NOT NULL,
    TITLE text NOT NULL,
    THEME text NOT NULL,
    PRICE bigint DEFAULT 0 NOT NULL,
    IMG_URL text NOT NULL,
    PRDT_URL text NOT NULL,
    MSG  text NOT NULL,
    RELEASE_DATE timestamp with time zone NOT NULL,
    REG_DATE timestamp with time zone DEFAULT now() NOT NULL
);

CREATE SEQUENCE product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE product_id_seq OWNED BY product.ID;

ALTER TABLE ONLY product ALTER COLUMN id SET DEFAULT nextval('product_id_seq'::regclass);

CREATE TABLE prdt_schedule (
    ID bigint NOT NULL,
    USER_ID bigint NOT NULL,
    PRDT_ID bigint NOT NULL,
    STATUS character varying(10) NOT NULL,
    MSG  text NOT NULL,
    REG_DATE timestamp with time zone DEFAULT now() NOT NULL
);

ALTER TABLE ONLY prdt_schedule ADD COLUMN SIZE character varying(12) DEFAULT '' NOT NULL;


CREATE SEQUENCE prdt_schedule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE prdt_schedule_id_seq OWNED BY prdt_schedule.ID;

ALTER TABLE ONLY prdt_schedule ALTER COLUMN ID SET DEFAULT nextval('prdt_schedule_id_seq'::regclass);
