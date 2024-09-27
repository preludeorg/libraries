package Cloud

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/cloudtrail"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
	"github.com/aws/aws-sdk-go-v2/service/rds"
	"github.com/aws/smithy-go"
)

func CheckError(err error) error {
	if err != nil {
		var ae smithy.APIError
		if errors.As(err, &ae) {
			if ae.ErrorCode() == "AccessDenied" {
				return fmt.Errorf("access denied by IAM")
			}
		}
		return err
	}
	return nil
}

func GetCloudTrailClient() (*cloudtrail.Client, error) {
	region := GetRegion()

	cfg, err := config.LoadDefaultConfig(context.TODO(),
		config.WithRegion(region),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to load AWS config: %v", err)
	}

	_, err = cfg.Credentials.Retrieve(context.TODO())
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve AWS credentials: %v", err)
	}

	return cloudtrail.NewFromConfig(cfg), nil
}

func GetEC2Client() (*ec2.Client, error) {
	region := GetRegion()

	cfg, err := config.LoadDefaultConfig(context.TODO(),
		config.WithRegion(region),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to load AWS config: %v", err)
	}

	_, err = cfg.Credentials.Retrieve(context.TODO())
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve AWS credentials: %v", err)
	}

	return ec2.NewFromConfig(cfg), nil
}

func GetRDSClient() (*rds.Client, error) {
	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithDefaultRegion("us-east-1"))
	if err != nil {
		return nil, err
	}
	return rds.NewFromConfig(cfg), nil
}

func GetRegion() string {
	httpClient := http.Client{
		Timeout: 3 * time.Second,
	}

	resp, err := httpClient.Get("http://169.254.169.254/latest/meta-data/placement/region")
	if err != nil || resp.StatusCode != http.StatusOK {
		return "us-east-1"
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "us-east-1"
	}

	return string(body)
}
