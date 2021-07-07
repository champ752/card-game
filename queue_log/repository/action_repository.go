package repository

import (
	"context"
	"gorm.io/gorm"
	"queue_log/entities"
)

type ActionRepository struct {
	db *gorm.DB
}

func NewActionRepository(db *gorm.DB) ActionRepository {
	return ActionRepository{db: db}
}


func (repo *ActionRepository) CreateAction(ctx context.Context, action entities.Action) (entities.Action, error) {
	if err := repo.db.WithContext(ctx).Create(&action).Error; err != nil {
		return action, err
	}
	return action, nil
}

func (repo *ActionRepository) FindActionByBoardID(ctx context.Context, boardID string) ([]entities.Action, error) {
	var result []entities.Action
	if err := repo.db.WithContext(ctx).Find(&result, "board_id = ?", boardID).Error; err != nil {
		return result, err
	}
	return result, nil
}