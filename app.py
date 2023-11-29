import os
import json
from flask import Flask, jsonify, Response, request
from flask_sqlalchemy import SQLAlchemy
from serializers import UserSchema, ChangeAccessSchema, AccessChangeHistorySchema, CreateUserSchema
from feed import USERS_DATA, ACCESS_DATA
from connection import create_connection
from sqlalchemy import exc, Sequence
from marshmallow import ValidationError
from utils import get_formatted_changes_string, OperationTypeEnum
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app, engine_options={"creator": create_connection})


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, Sequence("id_seq", start=1), primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    accesses = db.relationship("Access", backref="user", lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Access(db.Model):
    __tablename__ = "access_table"

    id = db.Column(db.Integer, Sequence("id_seq", start=1), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    resource = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class AccessChangeHistory(db.Model):
    __tablename__ = "access_changes_history"

    id = db.Column(db.Integer, Sequence("id_seq", start=1), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    operation = db.Column(db.Enum(OperationTypeEnum))
    changes = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.cli.command("create-objects")
def create_objects():
    try:
        db.session.bulk_save_objects([User(**user) for user in USERS_DATA])
        db.session.commit()
        db.session.bulk_save_objects([Access(**access) for access in ACCESS_DATA])
        db.session.commit()
    except (exc.IntegrityError, exc.PendingRollbackError):
        print("Objects already created")


@app.route("/users", methods=["GET"])
def get_all_tasks():
    return jsonify(
        {"users": UserSchema(many=True).dump(User.query.order_by(User.surname).all())}
    )


@app.route("/create_user", methods=["POST"])
def create_user():
    try:
        data = CreateUserSchema().load(request.json)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

    user = User(name=data.get("name"), surname=data.get("surname"))
    db.session.add(user)
    db.session.commit()

    db.session.add(Access(user_id=user.id, resource=data.get("resource")))
    db.session.commit()

    db.session.add(
        AccessChangeHistory(
            user_id=user.id,
            changes=json.dumps({"user": data}),
            operation=OperationTypeEnum.INSERT
        )
    )
    db.session.commit()

    return Response("User created", 201)


@app.route("/change_resource/<int:user_id>", methods=["PATCH"])
def change_resource(user_id: int):
    if not (user := User.query.get(user_id)):
        return Response("User does not exists", 404)

    try:
        data = ChangeAccessSchema().load(request.json)
    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400

    old_access = list(map(lambda access: access.to_dict(), user.accesses))
    user.accesses[0].resource = data.get("resource")
    new_access = list(map(lambda access: access.to_dict(), user.accesses))
    db.session.commit()

    db.session.add(
        AccessChangeHistory(
            user_id=user_id,
            operation=OperationTypeEnum.UPDATE,
            changes=get_formatted_changes_string(old_access, new_access),
        )
    )
    db.session.commit()

    return Response("Success", 204)


@app.route("/history", methods=["GET"])
def get_history():
    queryset = AccessChangeHistory.query
    if user_id := request.args.get("user_id"):
        queryset = queryset.filter_by(user_id=user_id)
    else:
        queryset = queryset.all()
    return jsonify(
        {"history": AccessChangeHistorySchema(many=True).dump(queryset)}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
