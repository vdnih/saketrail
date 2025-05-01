from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    aws_iam as iam,
    CfnOutput,
    Duration,
)
from constructs import Construct
import yaml
import os

def load_config(environment):
    # base_dir = saketrail ディレクトリ
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) )
    env_dir = environment
    if environment == 'production':
        env_dir = 'prod'
    common_path = os.path.join(base_dir, 'config', 'common', f'{env_dir}.yml')
    infra_path = os.path.join(base_dir, 'config', env_dir, 'frontend.yml')
    print("common_path:", common_path)
    print("infra_path:", infra_path)
    with open(common_path, 'r', encoding='utf-8') as f:
        common = yaml.safe_load(f)
    with open(infra_path, 'r', encoding='utf-8') as f:
        infra = yaml.safe_load(f)
    return {'common': common, 'infra': infra}

class AuthStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        environment: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = load_config(environment)
        domain_prefix = environment
        hosted_ui_domain = f"{domain_prefix}-saketrail"
        web_callback_url = f"https://{config['common']['domain']}/callback"
        mobile_callback_url = "saketrail://callback"

        # User Pool
        user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=f"{environment}-saketrail-user-pool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
            ),
            custom_attributes={
                "displayName": cognito.StringAttribute(min_len=1, max_len=50, mutable=True),
                "profileImageUrl": cognito.StringAttribute(min_len=0, max_len=200, mutable=True),
                "registeredAt": cognito.StringAttribute(min_len=0, max_len=30, mutable=False),
            },
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
                temp_password_validity=Duration.days(7),
            ),
            mfa=cognito.Mfa.OPTIONAL,
            mfa_second_factor=cognito.MfaSecondFactor(sms=True, otp=True),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
        )

        # Hosted UIドメイン
        user_pool.add_domain(
            "CognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=hosted_ui_domain
            )
        )

        # User Pool Client
        user_pool_client = user_pool.add_client(
            "UserPoolClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            generate_secret=False,
            o_auth=cognito.OAuthSettings(
                callback_urls=[
                    mobile_callback_url,
                    web_callback_url,
                ],
                logout_urls=[
                    f"https://{config['common']['domain']}/logout",
                ],
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                scopes=[
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.PROFILE,
                ],
            ),
        )

        # Identity Pool
        identity_pool = cognito.CfnIdentityPool(
            self,
            "IdentityPool",
            allow_unauthenticated_identities=False,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=user_pool_client.user_pool_client_id,
                    provider_name=user_pool.user_pool_provider_name,
                )
            ],
        )

        # IAMロール（認証ユーザー用）
        authenticated_role = iam.Role(
            self,
            "CognitoDefaultAuthenticatedRole",
            assumed_by=iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                {
                    "StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
                    "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "authenticated"},
                },
                "sts:AssumeRoleWithWebIdentity",
            ),
            description="Default role for authenticated users",
        )

        # Identity Pool Role Attachment
        cognito.CfnIdentityPoolRoleAttachment(
            self,
            "IdentityPoolRoleAttachment",
            identity_pool_id=identity_pool.ref,
            roles={"authenticated": authenticated_role.role_arn},
        )

        # Outputs
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
        CfnOutput(self, "IdentityPoolId", value=identity_pool.ref) 