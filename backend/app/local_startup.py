from app.core.helpers.local import add_additional_env_vars
import uvicorn

add_additional_env_vars()
if __name__ == "__main__":

    uvicorn.run("app.main:app", host="0.0.0.0", port=5050, reload=True)
