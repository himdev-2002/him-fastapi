CREATE OR REPLACE PACKAGE pkg_role IS
TYPE t_refcur IS REF CURSOR;

PROCEDURE create_role(
    p_grp_id IN  CHAR,
    p_grp_desc IN VARCHAR2,
    p_id IN  CHAR,
    p_name IN VARCHAR2,
    p_active IN NUMBER,
    p_lvl IN VARCHAR2,
    p_util_pt IN NUMBER DEFAULT 0,
    p_chrg_rt IN NUMBER DEFAULT 0,
    is_commit IN NUMBER DEFAULT 0,
    r_id OUT CHAR);

PROCEDURE delete_role_by_roleid(
	p_id IN CHAR,
	is_commit IN NUMBER DEFAULT 0);

PROCEDURE get_active_role_by_roleid(
	p_id IN CHAR,
	p_rc OUT t_refcur);

PROCEDURE list_roles(
	p_rc OUT t_refcur);

END pkg_role;


CREATE OR REPLACE PACKAGE BODY pkg_role IS

PROCEDURE create_role(p_grp_id IN  CHAR, p_grp_desc IN VARCHAR2, 
p_id IN  CHAR, p_name IN VARCHAR2, p_active IN NUMBER, p_lvl IN VARCHAR2, 
p_util_pt IN NUMBER DEFAULT 0, p_chrg_rt IN NUMBER DEFAULT 0, 
is_commit IN NUMBER DEFAULT 0, r_id OUT CHAR) IS
err_msg VARCHAR2(100);
BEGIN
err_msg:=NULL;
IF p_grp_id IS NULL OR LENGTH(p_grp_id) <1 THEN
	err_msg:='ROLE_GROUP_ID::too short (min 1 chars)';
	RAISE_APPLICATION_ERROR(-20001, err_msg);
ELSIF p_grp_desc IS NULL OR LENGTH(p_grp_desc) < 5 THEN
	err_msg:='ROLE_GROUP_DESC::too short (min 5 chars)';
	RAISE_APPLICATION_ERROR(-20002, err_msg);
ELSIF p_name IS NULL OR LENGTH(p_name) < 5 THEN
	err_msg:='ROLE_NAME::too short (min 5 chars)';
	RAISE_APPLICATION_ERROR(-20003, err_msg);
ELSIF p_active IS NULL OR p_active NOT IN (0,1) THEN
	err_msg:='ACTIVE::invalid value (only 1 or 0)';
	RAISE_APPLICATION_ERROR(-20004, err_msg);
ELSE
	INSERT INTO P_ROLE 
	(ROLE_GROUP_ID, ROLE_GROUP_DESC, ROLE_ID, ROLE_NAME, ACTIVE, 
	ROLE_LEVEL, ROLE_UTILIZATION_POINT, ROLE_CHARGING_RATE) 
	VALUES
	(p_grp_id, p_grp_desc, p_id, p_name, p_active, p_lvl, p_util_pt, p_chrg_rt)
	RETURNING ROLE_ID INTO r_id;

	IF is_commit = 1 THEN COMMIT;
	END IF;
END IF;
EXCEPTION
	WHEN OTHERS THEN
--		DBMS_OUTPUT.PUT_LINE('Error lain: ' || SQLCODE || ' - ' || SQLERRM);
		IF SQLCODE >= -20004 AND SQLCODE < -20000 THEN 
			RAISE_APPLICATION_ERROR(SQLCODE, err_msg);
		ELSE
			RAISE_APPLICATION_ERROR(-20000, 'create_role error: ' || SQLERRM);
		END IF;
END create_role;

PROCEDURE delete_role_by_roleid(p_id IN CHAR,is_commit IN NUMBER DEFAULT 0) IS
err_msg VARCHAR2(100);
BEGIN
err_msg:=NULL;
DELETE FROM P_ROLE WHERE ROLE_ID = p_id;
IF SQL%ROWCOUNT = 0 THEN
	err_msg:='delete_role: role not found: ' || p_id;
	RAISE_APPLICATION_ERROR(-20011, err_msg);
END IF;
IF is_commit = 1 THEN COMMIT;
END IF;
EXCEPTION
	WHEN OTHERS THEN
		IF SQLCODE >= -20011 AND SQLCODE < -20010 THEN 
			RAISE_APPLICATION_ERROR(SQLCODE, err_msg);
		ELSE
			RAISE_APPLICATION_ERROR(-20010, 'delete_role error: ' || SQLERRM);
		END IF;
END delete_role_by_roleid;

PROCEDURE get_active_role_by_roleid(p_id IN CHAR, p_rc OUT t_refcur) IS
BEGIN
OPEN p_rc FOR
	SELECT ROLE_GROUP_ID, ROLE_GROUP_DESC, ROLE_ID, ROLE_NAME, 
		ROLE_LEVEL, ROLE_UTILIZATION_POINT, ROLE_CHARGING_RATE
	FROM P_ROLE
	WHERE ROLE_ID = p_id AND ACTIVE = 1;
EXCEPTION
	WHEN OTHERS THEN
		RAISE_APPLICATION_ERROR(-20020, 'get_active_role_by_roleid error: ' || SQLERRM);
END get_active_role_by_roleid;

PROCEDURE list_roles(p_rc OUT t_refcur) IS
BEGIN
OPEN p_rc FOR
	SELECT *
	FROM P_ROLE
	ORDER BY ROLE_GROUP_ID,ROLE_ID,ROLE_NAME;
EXCEPTION
	WHEN OTHERS THEN
		RAISE_APPLICATION_ERROR(-20030, 'list_roles error: ' || SQLERRM);
END list_roles;
 
END pkg_role;