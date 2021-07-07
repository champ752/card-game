package http

import (
	"github.com/gin-gonic/gin"
	"queue_log/dto"
	"queue_log/usecase"
)

type handler struct {
	uc usecase.Usecase
}

func NewHandler(router *gin.RouterGroup, usecase usecase.Usecase) {
	h := &handler{usecase}

	router.POST("/board", h.CreateBoard)
	router.POST("/action", h.CreateAction)
	router.GET("/board-action/:userID", h.GetBoardAndAction)
}

func (h *handler) CreateBoard(c *gin.Context) {
	var payload dto.CreateBoardRequest
	if err := c.BindJSON(&payload); err != nil {
		return
	}
	response, err := h.uc.CreateBoard(c.Request.Context(), payload)
	if err != nil {
		c.JSON(422, dto.CreateBoardResponse{})
		return
	}
	c.JSON(201, response)
}
func (h *handler) CreateAction(c *gin.Context) {
	var payload dto.CreateActionRequest
	if err := c.BindJSON(&payload); err != nil {
		return
	}
	response, err := h.uc.CreateAction(c.Request.Context(), payload)
	if err != nil {
		c.JSON(422, dto.FindBoardAndActionResponse{})
		return
	}
	c.JSON(201, response)
}
func (h *handler) GetBoardAndAction(c *gin.Context) {
	userID := c.Param("userID")
	payload := dto.FindBoardAndActionRequest{UserID: userID}
	response, err := h.uc.FindBoardAndAction(c.Request.Context(), payload)
	if err != nil {
		c.JSON(400, err)
		return
	}
	c.JSON(200, response)

}
