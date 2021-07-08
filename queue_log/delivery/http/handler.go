package http

import (
	"github.com/gin-gonic/gin"
	"queue_log/dto"
	"queue_log/usecase"
)

type handler struct {
	uc usecase.Usecase
}

// NewHandler handler for restful
func NewHandler(router *gin.RouterGroup, usecase usecase.Usecase) {
	h := &handler{usecase}

	router.GET("/board-action/:userID", h.GetBoardAndAction)
	router.GET("/board-win/:boardID", h.UpdateWinBoard)
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

func (h *handler) UpdateWinBoard(c *gin.Context) {
	boardID := c.Param("boardID")
	payload := dto.UpdateWinBoardRequest{BoardID: boardID}
	err := h.uc.UpdateWinBoard(c.Request.Context(), payload)
	if err != nil {
		c.JSON(400, err)
		return
	}
	c.JSON(200, gin.H{
		"success": "true",
	})

}
