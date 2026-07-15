from fastapi import APIRouter, Depends
import controllers.user as user_controller
import middlewares.auth as auth_middleware

publicRouter = APIRouter()
privateRouter = APIRouter(dependencies=[Depends(auth_middleware.run)])
router = APIRouter()

privateRouter.add_api_route("/users", user_controller.list, methods=["GET"])
privateRouter.add_api_route("/users", user_controller.create, methods=["POST"])
privateRouter.add_api_route("/users/{id}", user_controller.update, methods=["PUT"])
privateRouter.add_api_route("/users/{id}", user_controller.remove, methods=["DELETE"])
publicRouter.add_api_route("/login", user_controller.login, methods=["POST"])

router.include_router(publicRouter)
router.include_router(privateRouter)
