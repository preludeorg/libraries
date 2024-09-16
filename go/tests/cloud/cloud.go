package Cloud

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/rds"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/cloudtrail"
	"github.com/aws/aws-sdk-go/service/ec2"
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

func GetCloudTrailClient() (*cloudtrail.CloudTrail, error) {
	region := GetRegion()

	session, err := session.NewSessionWithOptions(session.Options{
		Config: aws.Config{
			Region: aws.String(region),
		},
		SharedConfigState: session.SharedConfigEnable,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create AWS session: %v", err)
	}

	_, err = session.Config.Credentials.Get()
	if err != nil {
		return nil, fmt.Errorf("failed to get AWS credentials: %v", err)
	}

	return cloudtrail.New(session), nil
}

func GetEC2Client() (*ec2.EC2, error) {
	region := GetRegion()

	session, err := session.NewSessionWithOptions(session.Options{
		Config: aws.Config{
			Region: aws.String(region),
		},
		SharedConfigState: session.SharedConfigEnable,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create AWS session: %v", err)
	}

	_, err = session.Config.Credentials.Get()
	if err != nil {
		return nil, fmt.Errorf("failed to get AWS credentials: %v", err)
	}

	return ec2.New(session), nil
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
		return "us-east-2"
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "us-east-2"
	}

	return string(body)
}

func GetSession() (*session.Session, error) {
	session, err := session.NewSessionWithOptions(session.Options{
		Config: aws.Config{
			Region: aws.String(GetRegion()),
		},
		SharedConfigState: session.SharedConfigEnable,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to configure session: %v", err)
	}
	return session, nil
}
