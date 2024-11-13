from fastapi import FastAPI
from application.endpoints import router


app = FastAPI(title="Documents manager",
              description="Приложение fastapi_practice реализовано для успешного прохождения курса в школе IT-Mentior для дальнейшего трудоустройства на ЗП 200К. "
                          "Приложение реализовано для работы с документами. Поддерживает просмотр, загрузку, удаление и анализ документов.",
              version="1.0.1",
              contact={"name":"Max Kraev", "email":"kraev-1993@list.ru"},
              )

app.include_router(router)
