
        if djprofile:
            return jsonify({"msg": "Usuario ya tiene un perfil"})
        if account.role_id != 2:
            return jsonify({"msg": "usuario no es un DJ"})

            