package main

import (
	"github.com/gin-gonic/gin"
	"go.elastic.co/apm/module/apmgin"
	postgres "go.elastic.co/apm/module/apmgormv2/driver/postgres"
	"gorm.io/gorm"
	"queue_log/delivery/http"
	"queue_log/entities"
	"queue_log/repository"
	"queue_log/usecase"
)

func main() {
	db, err := gorm.Open(postgres.Open("postgresql://postgres:postgres@localhost:5445/postgres"), &gorm.Config{})
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
	g.Run()
	//bRepo.CreateBoard(context.TODO(), entities.Board{
	//	ID:         "test",
	//	BoardData:  "1,2,3,4,5",
	//	PlayBy:     "uuid-user",
	//})
	//board, err := bRepo.FindBoard(context.TODO(), "uuid-user")
	//if err != nil {
	//	panic(err)
	//}
	//log.Printf("%+v",board)
	//aRepo.CreateAction(context.TODO(), entities.Action{
	//	BoardId:    "test",
	//	Number:     "1",
	//})
	//aRepo.CreateAction(context.TODO(), entities.Action{
	//	BoardId:    "test",
	//	Number:     "2",
	//})
	//aRepo.CreateAction(context.TODO(), entities.Action{
	//	BoardId:    "test",
	//	Number:     "3",
	//})
}
