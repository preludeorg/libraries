package service

import (
	"encoding/json"
	"fmt"
	"github.com/preludeorg/detect-clients/go/probe/internal/hades"
	"github.com/preludeorg/detect-clients/go/probe/internal/util"
	"os"
)

type ProbeService struct {
	token         string
	accountId     string
	accountSecret string
	proc          *hades.Probe
}

type Actions interface {
	Start()
	Stop()
	Register(string)
}

func CreateService() *ProbeService {
	return &ProbeService{
		token:         os.Getenv("PRELUDE_TOKEN"),
		accountId:     os.Getenv("PRELUDE_ACCOUNT_ID"),
		accountSecret: os.Getenv("PRELUDE_ACCOUNT_SECRET"),
		proc:          nil,
	}
}

func (ps *ProbeService) Start() {
	ps.proc = hades.CreateProbe(ps.token)
	go ps.proc.Start()
}

func (ps *ProbeService) Stop() {
	ps.proc.Stop()
}

func (ps *ProbeService) Register(name ...string) error {
	var err error
	if len(name) < 1 {
		name = make([]string, 1)
		name[0], err = os.Hostname()
		if err != nil {
			return err
		}
	}
	api := fmt.Sprintf("%s/account/endpoint", util.GetEnv("PRELUDE_HQ", "https://detect.prelude.org"))
	headers := map[string]string{"account": ps.accountId, "token": ps.accountSecret, "Content-Type": "application/json"}
	data, err := json.Marshal(map[string]string{"id": name[0]})
	resp, err := util.Request(api, data, headers)
	ps.token = fmt.Sprintf("%s", resp)
	return nil
}
