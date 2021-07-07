package main

import (
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/streadway/amqp"
	"go.elastic.co/apm/module/apmgin"
	postgres "go.elastic.co/apm/module/apmgormv2/driver/postgres"
	"gorm.io/gorm"
	"log"
	"os"
	"queue_log/delivery/http"
	"queue_log/delivery/mq"
	"queue_log/entities"
	"queue_log/repository"
	"queue_log/usecase"
)

func initQueue() (*amqp.Connection, error) {
	rabbitMqConnection := os.Getenv("RABBIT_URL")
	rabbitMqPort := os.Getenv("RABBIT_PORT")

	conn, err := amqp.Dial("amqp://guest:guest@"+rabbitMqConnection+":"+rabbitMqPort+"/")
	if err != nil {
		return nil, err
	}
	return conn, nil
}


func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	dbConnection := os.Getenv("DB_CONNECTION")
	port := os.Getenv("PORT")

	db, err := gorm.Open(postgres.Open(dbConnection), &gorm.Config{})
	if err != nil {
		panic(err)
	}
	db.AutoMigrate(&entities.Board{},&entities.Action{})

	bRepo := repository.NewBoardRepository(db)
	aRepo := repository.NewActionRepository(db)
	uc := usecase.NewUsecase(aRepo, bRepo)
	g := gin.New()
	g.Use(apmgin.Middleware(g))
	apiGroup := g.Group("/api")
	http.NewHandler(apiGroup, *uc)
	go g.Run(":"+port)

	queue, err := initQueue()
	if err != nil {
		panic(err)
	}
	queueDelivery := mq.NewRabbitMqHandler(*uc, queue)
	forever := make(chan struct{}, 1)
	err = queueDelivery.StartConsume()
	if err != nil {
		log.Println(err)
	}
	<-forever
}
