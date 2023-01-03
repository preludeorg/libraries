package service

import (
	"encoding/json"
	"fmt"
	"github.com/preludeorg/libraries/go/probe/internal/hades"
	"github.com/preludeorg/libraries/go/probe/internal/util"
	"os"
)

type ProbeService struct {
	PreludeService string
	AccountId      string
	AccountSecret  string
	ProbeToken     string
	ProbeTags      []string
	ProbeName      string
	proc           *hades.Probe
}

type Actions interface {
	Start()
	Stop()
	Register(string)
}

func CreateService() *ProbeService {
	return &ProbeService{
		PreludeService: "https://detect.preludesecurity.com",
		ProbeToken:     util.GetEnv("PRELUDE_TOKEN", ""),
		AccountId:      util.GetEnv("PRELUDE_ACCOUNT_ID", ""),
		AccountSecret:  util.GetEnv("PRELUDE_ACCOUNT_SECRET", ""),
		ProbeTags:      []string{},
		ProbeName:      "",
		proc:           nil,
	}
}

func (ps *ProbeService) Start() {
	ps.proc = hades.CreateProbe(ps.ProbeToken, ps.PreludeService)
	go ps.proc.Start()
}

func (ps *ProbeService) Stop() {
	if ps.proc != nil {
		ps.proc.Stop()
	}
}

func (ps *ProbeService) Register() error {
	var err error
	if ps.ProbeName == "" {
		ps.ProbeName, err = os.Hostname()
		if err != nil {
			return err
		}
	}
	api := fmt.Sprintf("%s/account/endpoint", ps.PreludeService)
	headers := map[string]string{"account": ps.AccountId, "token": ps.AccountSecret, "Content-Type": "application/json"}
	data, err := json.Marshal(map[string]interface{}{"id": ps.ProbeName, "tags": ps.ProbeTags})
	resp, err := util.Post(api, data, headers)
	if err != nil {
		return err
	}
	ps.ProbeToken = fmt.Sprintf("%s", resp)
	return nil
}
