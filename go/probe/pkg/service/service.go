package service

import (
	"encoding/json"
	"fmt"
	"github.com/preludeorg/libraries/go/probe/internal/hades"
	"github.com/preludeorg/libraries/go/probe/internal/util"
	"os"
)

type ProbeService struct {
	HQ            string
	Token         string
	AccountId     string
	AccountSecret string
	proc          *hades.Probe
}

type Actions interface {
	Start()
	Stop()
	Register(string)
}

func CreateService() *ProbeService {
	return &ProbeService{
		HQ:            "https://detect.prelude.org",
		Token:         util.GetEnv("PRELUDE_TOKEN", ""),
		AccountId:     util.GetEnv("PRELUDE_ACCOUNT_ID", ""),
		AccountSecret: util.GetEnv("PRELUDE_ACCOUNT_SECRET", ""),
		proc:          nil,
	}
}

func (ps *ProbeService) Start() {
	ps.proc = hades.CreateProbe(ps.Token, ps.HQ)
	go ps.proc.Start()
}

func (ps *ProbeService) Stop() {
	if ps.proc != nil {
		ps.proc.Stop()
	}
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
	api := fmt.Sprintf("%s/account/endpoint", ps.HQ)
	headers := map[string]string{"account": ps.AccountId, "token": ps.AccountSecret, "Content-Type": "application/json"}
	data, err := json.Marshal(map[string]string{"id": name[0]})
	resp, err := util.Post(api, data, headers)
	if err != nil {
		return err
	}
	ps.Token = fmt.Sprintf("%s", resp)
	return nil
}
