import boto3

class NotificationService:
    def __init__(self, sns_topic_arn):
        """
        Initialize the NotificationService.

        :param sns_topic_arn: The ARN of the SNS topic to publish notifications.
        """
        self.sns_topic_arn = sns_topic_arn
        self.sns_client = boto3.client('sns')

    def notify_subscribers(self, notification, emails):
        """
        Notify the subscribers of changes to a marker.

        :param notification: The message to send out.
        :param emails: A list of subscriber email addresses.
        """
        for email in emails:
            try:
                self.sns_client.publish(
                    TopicArn=self.sns_topic_arn,
                    Message=notification,
                    Subject="Update From Change Observer",
                    MessageAttributes={
                        "email": {
                            "DataType": "String",
                            "StringValue": email
                        }
                    }
                )
            except Exception as e:
                raise RuntimeError(f"Failed to notify subscriber {email}: {e}") from e
