import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class NotificationService:
    def __init__(self, sns_topic_arn):
        """
        Initialize the NotificationService.

        :param sns_topic_arn: The ARN of the SNS topic to publish notifications.
        """
        self.sns_topic_arn = sns_topic_arn
        self.sns_client = boto3.client('sns')

    def notify_subscribers(self, marker_id, emails):
        """
        Notify the subscribers of changes to a marker.

        :param marker_id: The ID of the marker that changed.
        :param emails: A list of subscriber email addresses.
        """
        for email in emails:
            try:
                message = f"Marker {marker_id} has been updated."
                self.sns_client.publish(
                    TopicArn=self.sns_topic_arn,
                    Message=message,
                    Subject="Marker Update Notification",
                    MessageAttributes={
                        "email": {
                            "DataType": "String",
                            "StringValue": email
                        }
                    }
                )
                logger.info(f"Notification sent to {email} for marker {marker_id}.")
            except Exception as e:
                logger.error(f"Failed to notify {email}: {e}")
