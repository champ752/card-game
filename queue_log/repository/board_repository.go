package repository

import (
	"context"
	"gorm.io/gorm"
	"queue_log/entities"
)

type BoardRepository struct {
	db *gorm.DB
}

func NewBoardRepository(db *gorm.DB) BoardRepository {
	return BoardRepository{db: db}
}

func (repo *BoardRepository) CreateBoard(ctx context.Context, board entities.Board) (entities.Board, error) {
	if err := repo.db.WithContext(ctx).Create(&board).Error; err != nil {
		return board, err
	}
	return board, nil
}

func (repo *BoardRepository) UpdateBoard(ctx context.Context, boardID string) error {
	if err := repo.db.WithContext(ctx).Model(&entities.Board{}).Where( "id = ?", boardID).Update("is_win", true).Error; err != nil {
		return  err
	}
	return  nil
}

func (repo *BoardRepository) FindBoard(ctx context.Context, userID string) (entities.Board, error) {
	var result entities.Board
	if err := repo.db.WithContext(ctx).Model(&entities.Board{}).Where( "play_by = ?", userID).Order("created_at desc").First(&result).Error; err != nil {
		return result, err
	}
	return result, nil
}