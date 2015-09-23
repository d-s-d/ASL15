DROP TABLE messages CASCADE;
DROP TABLE clients CASCADE;
DROP TABLE queues CASCADE;

CREATE TABLE clients (c serial primary key);
CREATE TABLE queues (q serial primary key);

CREATE TABLE messages (
	m bigserial primary key,
	q int REFERENCES queues (q) ON DELETE CASCADE,
	s int REFERENCES clients (c) ON DELETE CASCADE CHECK (s>0) ,
	r int REFERENCES clients (c) ON DELETE CASCADE,
	t text);

-- pop/peek for a given queue
CREATE INDEX ON messages (q, r, m); 
CREATE INDEX ON messages (q, r, s, m);

-- global pop/peek
CREATE INDEX ON messages (r, m);
CREATE INDEX ON messages (r, s, m);

-- list
CREATE INDEX ON messages (r, q);

-- ## PHANTOM ENTRIES ##

INSERT INTO clients VALUES (0); -- the any user

-- ## FUNCTION DEFINITIONS ##

/*
peek_r
*/
CREATE OR REPLACE FUNCTION peek_r(__r int) RETURNS setof messages LANGUAGE plpgsql AS
$$
BEGIN
	-- leverage index (r, m)
  RETURN QUERY EXECUTE 'SELECT * FROM (SELECT * FROM messages WHERE r=0 ORDER BY m LIMIT 1) AS t UNION (SELECT * FROM messages WHERE r=$1 ORDER BY m LIMIT 1) ORDER BY m LIMIT 1' USING __r;
END;
$$;


CREATE OR REPLACE FUNCTION peek_r_s(__r int, __s int) RETURNS setof messages LANGUAGE plpgsql AS
$$
BEGIN
  -- leverage index (r, s, m)
  RETURN QUERY EXECUTE 'SELECT * FROM (SELECT * FROM messages WHERE r=0 AND s=$1 ORDER BY m LIMIT 1) AS t UNION (SELECT * FROM messages WHERE r=$2 AND S=$1 ORDER BY m LIMIT 1) ORDER BY m LIMIT 1' USING __s, __r;
END;
$$;


CREATE OR REPLACE FUNCTION peek(__r int, __q int,  __s int) RETURNS setof messages LANGUAGE plpgsql AS
$$
BEGIN
	IF __q = 0 THEN -- queue is unspecified
		IF __s = 0 THEN -- sender is unspecified
			RETURN NEXT peek_r(__r);
		ELSE
			RETURN NEXT peek_r_s(__r, __s);
		END IF;
	ELSE -- queue is specified
		IF __s = 0 THEN -- sender unspecified
			-- leverage index (q, r, m)
  		RETURN QUERY EXECUTE 'SELECT * FROM (SELECT * FROM messages WHERE q=$1 AND r=0 ORDER BY m LIMIT 1) AS t UNION (SELECT * FROM messages WHERE q=$1 AND r=$2 ORDER BY m LIMIT 1) ORDER BY m LIMIT 1' USING __q, __r;
		ELSE -- sender is specified 
			-- leverage index (q, r, s, m)
  		RETURN QUERY EXECUTE 'SELECT * FROM (SELECT * FROM messages WHERE q=$1 AND s=$3 AND r=0 ORDER BY m LIMIT 1) AS t UNION (SELECT * FROM messages WHERE q=$1 AND s=$3 AND r=$2 ORDER BY m LIMIT 1) ORDER BY m LIMIT 1' USING __q, __r, __s;
		END IF;
	END IF;
END;
$$;

CREATE OR REPLACE FUNCTION pop(__r int, __q int, __s int) RETURNS messages LANGUAGE plpgsql AS
$$
DECLARE
	rec messages;
BEGIN
	SELECT INTO rec * FROM peek(__r, __q, __s);
	EXECUTE 'DELETE FROM messages WHERE m=$1' USING rec.m;
	RETURN rec;
END;
$$;

CREATE OR REPLACE FUNCTION list_nonempty_queues(__r int) RETURNS setof queues LANGUAGE plpgsql AS
$$
BEGIN
	RETURN QUERY EXECUTE 'SELECT DISTINCT ON (q) q FROM messages WHERE r=$1 OR r=0 GROUP BY q ORDER BY q' USING __r;
END;
$$;

CREATE OR REPLACE FUNCTION register_client() RETURNS setof clients LANGUAGE plpgsql AS
$$
BEGIN
	RETURN QUERY EXECUTE 'INSERT INTO clients VALUES (default) RETURNING *';
END;
$$;

CREATE OR REPLACE FUNCTION remove_client(__c int) RETURNS setof clients LANGUAGE plpgsql AS
$$
BEGIN
	RETURN QUERY EXECUTE 'DELETE FROM clients WHERE c=$1 RETURNING *' USING __c;
END;
$$;

CREATE OR REPLACE FUNCTION create_queue() RETURNS setof queues LANGUAGE plpgsql AS
$$
BEGIN
	RETURN QUERY EXECUTE 'INSERT INTO queues VALUES (default) RETURNING *';
END;
$$;

CREATE OR REPLACE FUNCTION remove_queue(__q int) RETURNS setof queues LANGUAGE plpgsql AS
$$
BEGIN
	RETURN QUERY EXECUTE 'DELETE FROM queues WHERE q=$1 RETURNING q' USING __q;
END;
$$;

CREATE OR REPLACE FUNCTION list_queues() RETURNS setof queues LANGUAGE plpgsql AS
$$
BEGIN
	RETURN QUERY EXECUTE 'SELECT * FROM queues';
END;
$$;

CREATE OR REPLACE FUNCTION list_clients() RETURNS setof clients LANGUAGE plpgsql AS
$$
BEGIN
	RETURN QUERY EXECUTE 'SELECT * FROM clients';
END;
$$;

CREATE OR REPLACE FUNCTION send_message(__q int, __s int, __r int, __content text) RETURNS setof messages LANGUAGE plpgsql AS
$$
BEGIN
  RETURN QUERY EXECUTE 'INSERT INTO messages VALUES (default, $1, $2, $3, $4) RETURNING *' USING __q, __s, __r, __content;
END;
$$;
