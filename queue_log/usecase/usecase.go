package usecase

import (
	"context"
	"errors"
	"queue_log/dto"
	"queue_log/entities"
	"queue_log/repository"
)

type Usecase struct {
	actionRepo repository.ActionRepository
	boardRepo  repository.BoardRepository
}

func NewUsecase(actionRepo repository.ActionRepository, boardRepo repository.BoardRepository) *Usecase {
	return &Usecase{actionRepo: actionRepo, boardRepo: boardRepo}
}

func (uc Usecase) CreateAction(ctx context.Context, req dto.CreateActionRequest) (dto.CreateActionResponse, error) {
	_, err := uc.actionRepo.CreateAction(ctx, entities.Action{
		BoardId: req.BoardID,
		Number:  req.Number,
		ArrIdx: req.ArrIdx,
	})
	if err != nil {
		return dto.CreateActionResponse{}, err
	}
	return dto.CreateActionResponse{Status: true}, nil
}

func (uc Usecase) CreateBoard(ctx context.Context, req dto.CreateBoardRequest) (dto.CreateBoardResponse, error) {
	_, err := uc.boardRepo.CreateBoard(ctx, entities.Board{
		ID:        req.BoardID,
		BoardData: req.BoardData,
		PlayBy:    req.UserID,
	})
	if err != nil {
		return dto.CreateBoardResponse{}, err
	}
	return dto.CreateBoardResponse{Status: true}, nil
}

func (uc Usecase) FindBoardAndAction(ctx context.Context, req dto.FindBoardAndActionRequest) (dto.FindBoardAndActionResponse, error) {
	board, err := uc.boardRepo.FindBoard(ctx, req.UserID)
	if err != nil {
		return dto.FindBoardAndActionResponse{}, err
	}
	if board.IsWin || board.ID == ""  {
		return dto.FindBoardAndActionResponse{}, errors.New("no board to resume")
	}
	actions, err := uc.actionRepo.FindActionByBoardID(ctx, board.ID)
	if err != nil {
		return dto.FindBoardAndActionResponse{}, err
	}
	response := dto.FindBoardAndActionResponse{
		Status:    true,
		BoardID:   board.ID,
		UserID:    board.PlayBy,
		BoardData: board.BoardData,
		Actions:   []dto.Action{},
	}
	for _, action := range actions {
		response.Actions = append(response.Actions, dto.Action{
			Number: action.Number,
			ArrIdx: action.ArrIdx,
		})
	}
	return response, nil
}

func (uc Usecase) UpdateWinBoard(ctx context.Context, req dto.UpdateWinBoardRequest) error {
	err := uc.boardRepo.UpdateBoard(ctx, req.BoardID)
	if err != nil {
		return err
	}
	return nil
}