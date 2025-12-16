from flask_api import create_app


from apscheduler.schedulers.background import BackgroundScheduler
import atexit 

from flask_api.repositories.viagem_repo.viagem_repo import verificar_conclusao_viagem
from flask_api.repositories.manutencao_repo import verificar_conclusao_manutencao 
from flask_api.repositories.motorista_repo.motorista_repo import verificar_cnh_vencida_motoristas 
from flask_api.repositories.veiculo_repo.veiculo_repo import verificar_preventiva_urgente_veiculos 





app = create_app()


if __name__ == "__main__":
    
    # ------------------ Incialização do scheduler

    #Inicializa o BackgroundScheduler
    scheduler = BackgroundScheduler()

    #Adiciona a tarefa: Rodar todos os dias às 00:05 (meia-noite e 5 minutos)
    # scheduler.add_job(
    #     func=verificar_conclusao_manutencao, 
    #     trigger="cron", 
    #     hour=0, 
    #     minute=5,
    #     id='manutencao_diaria_job', 
    #     replace_existing=True
    # )
    
    scheduler.add_job(
    func=verificar_conclusao_manutencao, 
    trigger='interval', 
    hours=24

)
    scheduler.add_job(
    func=verificar_cnh_vencida_motoristas,
    trigger='interval',
    hours=24,
    id='cnh_vencida_verificacao',
    replace_existing=True
    )
    scheduler.add_job(
    func=verificar_conclusao_viagem,
    trigger='interval',
    hours=24,  # a cada 10 minutos
    id='viagens_verificacao',
    replace_existing=True
)
    scheduler.add_job(
    func=verificar_preventiva_urgente_veiculos,
    trigger='interval',
    hours=24,
    id='verificar_preventiva_urgente',
    replace_existing=True
    )
    #Inicia o agendador em uma thread separada
    scheduler.start()

    #REGISTRO DE ENCERRAMENTO (quando o servidor parar)
    atexit.register(lambda: scheduler.shutdown())

    # =======================================================
    
    # 6. Rodar o App Flask
    app.run(debug=True)