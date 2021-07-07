package entities

import "time"

type BaseEntity struct {
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	DeletedAt *time.Time `json:"deleted_at"`
}


type Board struct {
	ID string `gorm:"primary_key"`
	BoardData string `gorm:"column:board_data;not null"`
	PlayBy string `gorm:"column:play_by;not null"`
	IsWin bool `gorm:"column:is_win"`
	BaseEntity
}

func (b Board) TableName() string {
	return "boards"
}


type Action struct {
	ID int `gorm:"primaryKey"`
	BoardId string `gorm:"column:board_id"`
	Number int `gorm:"column:number"`
	ArrIdx int `gorm:"column:arr_idx"`
	BaseEntity
}

func (b Action) TableName() string {
	return "actions"
}