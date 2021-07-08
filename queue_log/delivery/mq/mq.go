package mq

import (
	"context"
	"encoding/json"
	"github.com/streadway/amqp"
	"log"
	"queue_log/dto"
	"queue_log/usecase"
	"time"
)

type RabbitMqHandler struct {
	usecase usecase.Usecase
	conn *amqp.Connection
	stoppedErr chan error
}


func CreateHandler(ch *amqp.Channel, queueName, consumerName string, fn func(amqp.Delivery)) {

	log.Printf("consumer %s\n has begun", consumerName)

	msgs, err := ch.Consume(
		queueName,
		consumerName,
		false,
		false,
		false,
		false,
		nil,
	)

	if err != nil {
		log.Println(err)
		return
	}

	for msg := range msgs {
		go func(msg amqp.Delivery) {
			fn(msg)
		}(msg)
	}
}

func NewRabbitMqHandler(usecase usecase.Usecase, conn *amqp.Connection) *RabbitMqHandler {
	return &RabbitMqHandler{usecase: usecase, conn: conn}
}

func (h RabbitMqHandler) StartConsume() error{
	go h.consumeCreateAction()
	go h.consumeCreateBoard()
	return <-h.stoppedErr
}

func (h RabbitMqHandler) consumeCreateAction() {
	queueName := "create_action"
	ch, err := h.conn.Channel()
	if err != nil {
		h.stoppedErr <- err
		return
	}
	_, err = ch.QueueDeclare(
		queueName, // name
		false,     // durable
		false,     // delete when unused
		false,     // exclusive
		false,     // no-wait
		nil,       // arguments
	)
	if err != nil {
		h.stoppedErr <- err
		return
	}
	CreateHandler(ch, queueName, "queue-01", h.handleCreateAction)

}


func (h RabbitMqHandler) handleCreateAction(d amqp.Delivery) {
	var data dto.CreateActionRequest
	if err := json.Unmarshal(d.Body, &data); err != nil {
		log.Println(err)
		d.Reject(false)
		return
	}
	log.Printf("in coming create action %+v \n", data)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
	defer cancel()

	if _, err := h.usecase.CreateAction(ctx, data); err != nil{
		log.Println(err)
	}
	d.Ack(false)
}



func (h RabbitMqHandler) consumeCreateBoard() {
	queueName := "create_board"
	ch, err := h.conn.Channel()
	if err != nil {
		h.stoppedErr <- err
		return
	}
	_, err = ch.QueueDeclare(
		queueName, // name
		false,     // durable
		false,     // delete when unused
		false,     // exclusive
		false,     // no-wait
		nil,       // arguments
	)
	if err != nil {
		h.stoppedErr <- err
		return
	}
	CreateHandler(ch, queueName, "queue-01", h.handleCreateBoard)

}


func (h RabbitMqHandler) handleCreateBoard(d amqp.Delivery) {
	var data dto.CreateBoardRequest
	if err := json.Unmarshal(d.Body, &data); err != nil {
		log.Println(err)
		d.Reject(false)
		return
	}
	log.Printf("in coming create board %+v \n", data)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second*5)
	defer cancel()

	if _, err := h.usecase.CreateBoard(ctx, data); err != nil{
		log.Println(err)
	}
	d.Ack(false)
}