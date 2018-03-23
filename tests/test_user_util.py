#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `user_util` package."""

import pytest
from types import GeneratorType

from click.testing import CliRunner

from user_util import user_util
from user_util import cli

VALID_SALT_LIST_ONE_SALT = ['gsw@&2p)$^p2hdk&ou0e%c=ou80o=%!+tv7(u(ircv@+96jl6$']
VALID_SALT_LIST_THREE_SALTS = [
    '^==!0%=z4s!v7!yl0#+m6-st^*946aop6$0i+hu13&h_$a$vq8',
    'wdwh&#8s@(f=jnlky4up8p0#04t$jp%ip)nfp@de6rr9i)j7nf',
    ')h1^pu8a!rh=%$_4f7sx*5^46ln_pujw6y*s0=dl6i$_#&#io1',
]
VALID_SALT_LIST_FIVE_SALTS = [
    '8rv!7iy4a7mdvs_kudis6&oycj0_b(mj0s^@*e5p)(o+m(c-cb',
    'xp)43m+d_!f!-)c=ki_8oc2w9(^r^umy73%dp@z7sknn#800z$',
    'some_salt_that_is_not_very_random',
    '$=ldtvagk$qwc)cz%2%edaa_id45^(xg*1rs#t0inywla*)3+x',
    '4eyp*!%nz&g@8(tm!236ykbg2xzwcix!=)06q&=d2rh@3n1o+8',
]
VALID_SALT_LISTS = (
    VALID_SALT_LIST_ONE_SALT,
    VALID_SALT_LIST_THREE_SALTS,
    VALID_SALT_LIST_FIVE_SALTS,
)
INVALID_SALT_LIST = (
    'gsw@&2p)$^p2hdk&ou0e%c=ou80o=%!+tv7(u(ircv@+96jl6$',
    None,
    [],
)


def test_command_line_interface():
    """
    Test the CLI.
    """
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'user_util.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output

#
# Username retirement tests
#

@pytest.mark.parametrize('salt_list', VALID_SALT_LISTS)
def test_username_to_hash(salt_list):
    username = 'ALearnerUserName'
    retired_username = user_util.get_retired_username(username, salt_list)
    assert retired_username != username
    assert retired_username.startswith('_'.join(user_util.RETIRED_USERNAME_DEFAULT_FMT.split('_')[0:-1]))
    # Since SHA1 is used, the hexadecimal digest length should be 40.
    assert len(retired_username.split('_')[-1]) == 40


@pytest.mark.parametrize('salt_list', (VALID_SALT_LIST_THREE_SALTS,))
def test_correct_username_hash(salt_list):
    """
    Verify that get_retired_username uses the current salt and returns the expected hash.
    """
    username = 'ALearnerUserName'
    # Valid retired usernames for the above username when using VALID_SALT_LIST_THREE_SALTS.
    valid_retired_usernames = [
        user_util.RETIRED_USERNAME_DEFAULT_FMT.format(user_util._compute_retired_hash(username, salt))
        for salt in salt_list
    ]
    retired_username = user_util.get_retired_username(username, salt_list)
    assert retired_username == valid_retired_usernames[-1]


@pytest.mark.parametrize('salt_list', (VALID_SALT_LIST_FIVE_SALTS,))
def test_all_usernames_to_hash(salt_list):
    username = 'ALearnerUserName'
    retired_username_generator = user_util.get_all_retired_usernames(username, salt_list)
    assert isinstance(retired_username_generator, GeneratorType)
    assert len(list(retired_username_generator)) == len(VALID_SALT_LIST_FIVE_SALTS)


@pytest.mark.parametrize('salt_list', VALID_SALT_LISTS)
def test_username_to_hash_with_different_format(salt_list):
    username = 'ALearnerUserName'
    retired_username_fmt = "{}_is_now_the_retired_username"
    retired_username = user_util.get_retired_username(username, salt_list, retired_username_fmt=retired_username_fmt)
    assert retired_username.endswith('_'.join(retired_username_fmt.split('_')[1:]))
    # Since SHA1 is used, the hexadecimal digest length should be 40.
    assert len(retired_username.split('_')[0]) == 40

#
# Email address retirement tests
#

@pytest.mark.parametrize('salt_list', VALID_SALT_LISTS)
def test_email_to_hash(salt_list):
    email = 'a.learner@example.com'
    retired_email = user_util.get_retired_email(email, salt_list)
    assert retired_email != email
    assert retired_email.startswith('_'.join(user_util.RETIRED_EMAIL_DEFAULT_FMT.split('_')[0:2]))
    assert retired_email.endswith(user_util.RETIRED_EMAIL_DEFAULT_FMT.split('@')[-1])
    # Since SHA1 is used, the hexadecimal digest length should be 40.
    assert len(retired_email.split('@')[0]) == len('retired_email_') + 40


@pytest.mark.parametrize('salt_list', (VALID_SALT_LIST_THREE_SALTS,))
def test_correct_email_hash(salt_list):
    """
    Verify that get_retired_username uses the current salt and returns the expected hash.
    """
    email = 'a.learner@example.com'
    # Valid retired emails for the above email address when using VALID_SALT_LIST_THREE_SALTS.
    valid_retired_emails = [
        user_util.RETIRED_EMAIL_DEFAULT_FMT.format(user_util._compute_retired_hash(email, salt))
        for salt in salt_list
    ]
    retired_email = user_util.get_retired_email(email, salt_list)
    assert retired_email == valid_retired_emails[-1]


@pytest.mark.parametrize('salt_list', (VALID_SALT_LIST_FIVE_SALTS,))
def test_all_emails_to_hash(salt_list):
    email = 'a.learner@example.com'
    retired_email_generator = user_util.get_all_retired_emails(email, salt_list)
    assert isinstance(retired_email_generator, GeneratorType)
    assert len(list(retired_email_generator)) == len(VALID_SALT_LIST_FIVE_SALTS)


@pytest.mark.parametrize('salt_list', VALID_SALT_LISTS)
def test_email_to_hash_with_different_format(salt_list):
    email = 'a.learner@example.com'
    retired_email_fmt = "{}_is_now_the_retired_email@devnull.example.com"
    retired_username = user_util.get_retired_email(email, salt_list, retired_email_fmt=retired_email_fmt)
    assert retired_username.endswith('_'.join(retired_email_fmt.split('_')[1:]))
    # Since SHA1 is used, the hexadecimal digest length should be 40.
    assert len(retired_username.split('_')[0]) == 40

#
# Bad salt tests.
#

@pytest.mark.parametrize('salt', INVALID_SALT_LIST)
def test_username_to_hash_bad_salt(salt):
    """
    Salts that are *not* lists/tuples should fail.
    """
    with pytest.raises((ValueError, IndexError)):
        retired_username = user_util.get_retired_username('AnotherLearnerUserName', salt)
