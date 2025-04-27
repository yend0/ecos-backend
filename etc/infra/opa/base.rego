package test

import rego.v1

import future.keywords.if

default allow := false


allow = true if {
    permissions = {
        {
            "method": "GET",
            "path": ["api", "v1", "users", "verify-email", "*"],
            "roles": [""]
        },
        {
            "method": "GET",
            "path": ["api", "v1", "users", "profile"],
            "roles": ["user", "moderator"]
        },
        {
            "method": "POST",
            "path": ["api", "v1", "users", "sign-up"],
            "roles": [""]
        },
        {
            "method": "PATCH",
            "path": ["api", "v1", "users", "profile"],
            "roles": ["user", "moderator"]
        },
        {
            "method": "PATCH",
            "path": ["api", "v1", "reception-points", "*", "status"],
            "roles": ["moderator"]
        },
        {
            "method": "DELETE",
            "path": ["api", "v1", "reception-points", "*", "wastes", "*"],
            "roles": ["moderator"]
        },
        {
            "method": "POST",
            "path": ["api", "v1", "reception-points", "*", "wastes", "*"],
            "roles": ["user", "moderator"]
        },
        {
            "method": "GET",
            "path": ["api", "v1", "reception-points"],
            "roles": ["", "user", "moderator"]
        },
        {
            "method": "POST",
            "path": ["api", "v1", "reception-points"],
            "roles": ["user", "moderator"]
        },
        {
            "method": "DELETE",
            "path": ["api", "v1", "reception-points", "*"],
            "roles": ["moderator"]
        },
        {
            "method": "GET",
            "path": ["api", "v1", "moderations"],
            "roles": ["moderator"]
        },
        {
            "method": "GET",
            "path": ["api", "v1", "wastes"],
            "roles": ["", "user", "moderator"]
        },
        {
            "method": "POST",
            "path": ["api", "v1", "wastes"],
            "roles": ["moderator"]
        },
        {
            "method": "DELETE",
            "path": ["api", "v1", "wastes", "*"],
            "roles": ["moderator"]
        },
        {
            "method": "GET",
            "path": ["api", "v1", "waste-translations"],
            "roles": ["", "user", "moderator"]
        },
        {
            "method": "POST",
            "path": ["api", "v1", "waste-translations"],
            "roles": ["moderator"]
        },
        {
            "method": "DELETE",
            "path": ["api", "v1", "waste-translations", "*"],
            "roles": ["moderator"]
        },
        {
            "method": "PATCH",
            "path": ["api", "v1", "waste-translations", "*"],
            "roles": ["moderator"]
        }
    }
    p := permissions[_]
    p.method = input.method
    p.path = input.path
    role := input.roles[_]
    role = p.roles[_]
}