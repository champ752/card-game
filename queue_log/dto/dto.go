package dto


type CreateActionRequest struct {
	BoardID string `json:"board_id" binding:"required"`
	Number int `json:"number" binding:"required"`
	ArrIdx int `json:"arr_idx" binding:"required"`
}

type CreateActionResponse struct {
	Status bool `json:"status"`
}


type CreateBoardRequest struct {
	BoardID string `json:"board_id" binding:"required"`
	UserID string `json:"user_id" binding:"required"`
	BoardData string `json:"board_data" binding:"required"`
}

type CreateBoardResponse struct {
	Status bool `json:"status"`
}

type FindBoardAndActionRequest struct {
	UserID string `json:"user_id"`
}

type Action struct {
	Number int `json:"number"`
	ArrIdx int `json:"arr_idx"`
}

type FindBoardAndActionResponse struct {
	Status bool `json:"status"`
	BoardID string `json:"board_id,omitempty"`
	UserID string `json:"user_id,omitempty"`
	BoardData string `json:"board_data,omitempty"`
	Actions []Action `json:"actions"`
}

type UpdateWinBoardRequest struct {
	BoardID string `json:"board_id"`
}