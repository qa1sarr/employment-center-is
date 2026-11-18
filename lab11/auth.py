# auth.py — жүйеге кіру (логин + пароль): ОСАЛ және ҚАУІПСІЗ нұсқа.
# Пароль жобадағыдай SHA-256 хэшімен сақталады.
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def build_login_query_vulnerable(email, password):
    # ҚАТЕ: логин SQL мәтініне тікелей қосылады
    return (
        "SELECT user_id, full_name, email, role FROM users "
        "WHERE email = '" + email + "' "
        "AND password_hash = '" + hash_password(password) + "'"
    )


def login_vulnerable(conn, email, password):
    query = build_login_query_vulnerable(email, password)
    row = conn.cursor().execute(query).fetchone()
    return query, row


LOGIN_SECURE_QUERY = (
    "SELECT user_id, full_name, email, role FROM users "
    "WHERE email = ? AND password_hash = ?"
)


def login_secure(conn, email, password):
    row = conn.cursor().execute(
        LOGIN_SECURE_QUERY, (email, hash_password(password))
    ).fetchone()
    return LOGIN_SECURE_QUERY, row
