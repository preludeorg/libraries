package hades

import (
	"encoding/hex"
	"fmt"
	"github.com/preludorg/detect-clients/go/probe/internal/util"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"syscall"
	"time"
)

type Probe struct {
	signals chan bool
	token   string
	hq      string
	dos     string
	sleep   time.Duration
	cwd     string
}

type Actions interface {
	Start()
	Stop()
	runTask([]byte)
	run(string) int
	save([]byte) (*os.File, error)
	resourceUsage() time.Duration
}

func CreateProbe(token string) *Probe {
	wd, err := util.FindWorkingDirectory()
	if err != nil {
		panic(err)
	}
	return &Probe{
		signals: make(chan bool),
		token:   token,
		hq:      util.GetEnv("PRELUDE_HQ", "https://detect.prelude.org"),
		dos:     fmt.Sprintf("%s-%s.exe", runtime.GOOS, runtime.GOARCH),
		sleep:   43200 * time.Second,
		cwd:     wd,
	}
}

func (p *Probe) Start() {
	for {
		p.runTask([]byte(p.dos))
		select {
		case <-p.signals:
			return
		case <-time.After(p.sleep):
			continue
		}
	}
}

func (p *Probe) Stop() {
	p.signals <- true
}

func (p *Probe) runTask(data []byte) {
	if resp, err := util.Request(fmt.Sprintf("%s", p.hq), data, map[string]string{"token": p.token, "Content-Type": "application/x-www-form-urlencoded"}); err == nil && len(resp) > 0 {
		pre := p.resourceUsage()
		id := resp[:36]
		exe, err := p.save(resp[36:])
		if err == nil {
			result := p.run(exe)
			_ = os.Remove(exe.Name())
			post := p.resourceUsage()
			p.runTask([]byte(fmt.Sprintf("%s:%s:%d:%0.5f", p.dos, id, result, (post - pre).Seconds())))
		}
	}
}

func (p *Probe) save(data []byte) (*os.File, error) {
	f, err := os.CreateTemp(p.cwd, "detect")
	if err != nil {
		return nil, err
	}

	decoded, err := hex.DecodeString(string(data))
	if err != nil {
		return nil, err
	}

	if _, err := f.Write(decoded); err != nil {
		return nil, err
	}

	if err := f.Close(); err != nil {
		return nil, err
	}

	err = os.Chmod(f.Name(), 0500)
	if err != nil {
		return nil, err
	}

	return f, nil
}

func (p *Probe) run(exe *os.File) int {
	out, err := exec.Command(exe.Name(), "attack").Output()
	if err != nil {
		return 3
	}
	exec.Command(exe.Name(), "cleanup").Run()
	intVal, err := strconv.Atoi(fmt.Sprintf("%s", out))
	return intVal
}

func (p *Probe) resourceUsage() time.Duration {
	var rusage syscall.Rusage
	if err := syscall.Getrusage(syscall.RUSAGE_SELF, &rusage); err == nil {
		return time.Duration(rusage.Utime.Nano() + rusage.Stime.Nano())
	}
	return time.Duration(0)
}
