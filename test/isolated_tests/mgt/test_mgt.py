import pytest
from unittest import mock 

from yosai import (
    DefaultAuthenticator,
    DefaultSecurityManager,
    DefaultSubjectContext,
    IllegalArgumentException,
    ModularRealmAuthorizer,
    cache_abcs,
)

from ..session.doubles import (
    MockDefaultSessionManager,
)

from .doubles import (
    MockRememberMeManager,
)


def test_dsm_setauthenticator_da(
        default_security_manager, default_authenticator, monkeypatch):
    """
    unit tested:  authenticator.setter

    test case:
    when authenticator=DefaultAuthenticator, then dsm.authenticator.realms is 
    set to self.realms and then eventbus and cachemanager are set for it
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'realms', 'verified') 
    da = default_authenticator

    with mock.patch.object(DefaultSecurityManager,
                           'apply_event_bus') as mock_aev:
        mock_aev.return_value = None

        with mock.patch.object(DefaultSecurityManager,
                               'apply_cache_manager') as mock_acm:
            mock_acm.return_value = None 
            dsm.authenticator = da

            mock_aev.assert_called_once_with(da)
            mock_acm.assert_called_once_with(da)
            
            assert dsm.authenticator.realms == 'verified' 

def test_dsm_setauthenticator_raises(
        default_security_manager, default_authenticator, monkeypatch):
    """
    unit tested:  authenticator.setter

    test case: 
    passing None as an argument value raises an exception
    """
    dsm = default_security_manager

    with pytest.raises(IllegalArgumentException):
        dsm.authenticator = None    

def test_dsm_setauthorizer(default_security_manager):
    """
    unit tested:  authorizer.setter

    test case:  setting an authorizer attribute in turn applies an event_bus
                and cache_manager to it
    """
    dsm = default_security_manager

    with mock.patch.object(DefaultSecurityManager,
                           'apply_event_bus') as mock_aev:
        mock_aev.return_value = None

        with mock.patch.object(DefaultSecurityManager,
                               'apply_cache_manager') as mock_acm:
            mock_acm.return_value = None 
            dsm.authorizer = 'authorizer'

            mock_aev.assert_called_once_with(dsm.authorizer)
            mock_acm.assert_called_once_with(dsm.authorizer)
            
            assert dsm.authorizer == 'authorizer'

def test_dsm_setauthorizer_raises(default_security_manager):
    """
    unit tested:  authorizer.setter

    test case:
    passing None as an argument value raises an exception
    """
    dsm = default_security_manager

    with pytest.raises(IllegalArgumentException):
        dsm.authorizer = None


def test_dsm_set_cachemanager(default_security_manager):
    """
    unit tested:  cache_manager.setter

    test case:
    sets cache_manager attribute and then applies the cachemanager to its 
    related objects (those that implement the CacheManagerAware interface)
    """
    dsm = default_security_manager

    with mock.patch.object(DefaultSecurityManager,
                           'get_dependencies_for_injection') as dsm_gdfi:
        dsm_gdfi.return_value = {'val1', 'val2'}
        with mock.patch.object(DefaultSecurityManager,
                               'apply_cache_manager') as dsm_acm:
            dsm_acm.return_value = None

            dsm.cache_manager = 'cachemanager'

            dsm_gdfi.assert_called_once_with('cachemanager')
            assert dsm_acm.called and dsm.cache_manager == 'cachemanager'

def test_dsm_set_cachemanager_raises(default_security_manager):
    """
    unit tested:  cache_manager.setter

    test case:  
    passing None as an argument value raises an exception
    """
    dsm = default_security_manager

    with pytest.raises(IllegalArgumentException):
        dsm.cache_manager = None

def test_dsm_set_eventbus(default_security_manager):
    """
    unit tested:  event_bus.setter

    test case:  
    sets attribute and calls method
    """
    dsm = default_security_manager
    with mock.patch.object(DefaultSecurityManager,
                           'get_dependencies_for_injection') as dsm_gdfi:
        dsm_gdfi.return_value = {'val1', 'val2'}
        with mock.patch.object(DefaultSecurityManager,
                               'apply_event_bus') as dsm_aeb:
            dsm_aeb.return_value = None

            dsm.event_bus = 'eventbus'

            dsm_gdfi.assert_called_once_with('eventbus')
            assert dsm_aeb.called and dsm.event_bus == 'eventbus'


def test_dsm_set_eventbus_raises(default_security_manager):
    """
    unit tested:  event_bus.setter

    test case:
    passing None as an argument value raises an exception
    """
    dsm = default_security_manager

    with pytest.raises(IllegalArgumentException):
        dsm.event_bus = None


@pytest.mark.parametrize(
    'authenticator, expected_authc_realms, authorizer, expected_authz_realms',
    [(DefaultAuthenticator(event_bus='eventbus'), 'realms', 
     ModularRealmAuthorizer(), 'realms'),
     (type('DumbAuthenticator', (object,), {'realms': None})(), None,
      type('DumbAuthorizer', (object,), {'realms': None})(), None)])
def test_set_realms(
        default_security_manager, authenticator, expected_authc_realms, 
        authorizer, expected_authz_realms, monkeypatch):
    """
    unit tested:  set_realms

    test case:
    applies eventbus and cachemanager to eligible realms, then tries to assign 
    realms to the authenticator and authorizer
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'authenticator', authenticator) 
    monkeypatch.setattr(dsm, 'authorizer', authorizer) 

    with mock.patch.object(DefaultSecurityManager,
                           'apply_event_bus') as dsm_aeb:
        dsm_aeb.return_value = None
        with mock.patch.object(DefaultSecurityManager,
                               'apply_cache_manager') as dsm_acm:
            dsm_acm.return_value = None

            dsm.set_realms('realms')

            dsm_aeb.assert_called_once_with('realms')
            dsm_acm.assert_called_once_with('realms')
            assert (dsm.authenticator.realms == expected_authc_realms and 
                    dsm.authorizer.realms == expected_authz_realms)

def test_set_realms_raises(default_security_manager):
    """
    unit tested:  set_realms

    test case:
    passing None as an argument value raises an exception
    """
    dsm = default_security_manager

    with pytest.raises(IllegalArgumentException):
        dsm.set_realms(None)

def test_apply_targets_single(default_security_manager):
    """
    unit tested:  apply_targets 

    test case:
    passing a single value results in using except block logic and a single call
    """
    dsm = default_security_manager
    va = mock.MagicMock()
    dc = type('DumbClass', (object,), {})()
    dsm.apply_target_s(va, dc) 
    va.assert_called_once_with(dc)

def test_apply_targets_collection(default_security_manager):
    """
    unit tested:  apply_targets 

    test case:
    passing a collection results in using try block logic and iterative calls 
    """
    dsm = default_security_manager
    va = mock.MagicMock()
    dc = type('DumbClass', (object,), {})
    mylist = [dc(), dc(), dc()]

    dsm.apply_target_s(va, mylist) 

    calls = [mock.call(mylist[0]), mock.call(mylist[1]), mock.call(mylist[2])] 
    assert calls in va.call_args_list  

def test_apply_cache_manager(default_security_manager):
    """
    unit tested:  apply_cache_manager

    test case:
    calls apply_target_s with inner function 
    """
    dsm = default_security_manager

    with mock.patch.object(dsm, 'apply_target_s') as dsm_ats:
        dsm_ats.return_value = None

        dsm.apply_cache_manager('target1')

        assert 'target1' in dsm_ats.call_args[0]

def test_apply_eventbus(default_security_manager):
    """
    unit tested:  apply_event_bus

    test case:
    calls apply_target_s with inner function 
    """
    dsm = default_security_manager

    with mock.patch.object(dsm, 'apply_target_s') as dsm_ats:
        dsm_ats.return_value = None

        dsm.apply_event_bus('target1')

        assert 'target1' in dsm_ats.call_args[0]

def test_dsm_get_dependencies_for_injection(default_security_manager):
    """
    unit tested:  get_dependencies_for_injection

    test case:
    ignores the argument passed, returns the rest of the dependents
    """
    dsm = default_security_manager
    result = dsm.get_dependencies_for_injection(dsm._event_bus)
    assert dsm._event_bus not in result

def test_dsm_get_dependencies_for_injection_raises(
        default_security_manager, dependencies_for_injection):
    """
    unit tested:  get_dependencies_for_injection

    test case:
    fails to find the argument passed, returns all of the dependents
    """
    dsm = default_security_manager
    dc = type('DumbClass', (object,), {})
    result = dsm.get_dependencies_for_injection(dc)
    assert result == dependencies_for_injection 


def test_dsm_authenticate_account(
        default_security_manager, username_password_token):
    """
    unit tested:  authenticate_account

    test case:
    passes request on to authenticator
    """
    dsm = default_security_manager
    upt = username_password_token
    with mock.patch.object(DefaultAuthenticator,
                           'authenticate_account') as da_aa:
        dsm.authenticate_account(upt)
        da_aa.assert_called_once_with(upt)

def test_dsm_is_permitted(default_security_manager):
    """
    unit tested:  is_permitted

    test case:
    passes request on to authorizer
    """
    dsm = default_security_manager
    with mock.patch.object(ModularRealmAuthorizer, 'is_permitted') as mra_ip:
        dsm.is_permitted('identifiers', 'permission_s')
        mra_ip.assert_called_once_with('identifiers', 'permission_s')


def test_dsm_is_permitted_all(default_security_manager):
    """
    unit tested: is_permitted_all

    test case:  
    passes request on to authorizer
    """
    dsm = default_security_manager
    with mock.patch.object(ModularRealmAuthorizer, 'is_permitted_all') as mra_ipa:
        dsm.is_permitted_all('identifiers', 'permission_s')
        mra_ipa.assert_called_once_with('identifiers', 'permission_s')


def test_dsm_check_permission(default_security_manager):
    """
    unit tested:  check_permission

    test case:  
    passes request on to authorizer
    """
    dsm = default_security_manager
    with mock.patch.object(ModularRealmAuthorizer, 'check_permission') as mra_cp:
        dsm.check_permission('identifiers', 'permission_s')
        mra_cp.assert_called_once_with('identifiers', 'permission_s')


def test_dsm_has_role(default_security_manager):
    """
    unit tested:  has_role

    test case:
    passes request on to authorizer
    """
    dsm = default_security_manager
    with mock.patch.object(ModularRealmAuthorizer, 'has_role') as mra_hr:
        dsm.has_role('identifiers', 'permission_s')
        mra_hr.assert_called_once_with('identifiers', 'permission_s')


def test_dsm_has_all_roles(default_security_manager):
    """
    unit tested:  has_all_roles

    test case:
    passes request on to authorizer
    """
    dsm = default_security_manager
    with mock.patch.object(ModularRealmAuthorizer, 'has_all_roles') as mra_har:
        dsm.has_all_roles('identifiers', 'permission_s')
        mra_har.assert_called_once_with('identifiers', 'permission_s')


def test_dsm_check_role(default_security_manager):
    """
    unit tested:  check_role 

    test case:
    passes request on to authorizer
    """
    dsm = default_security_manager
    with mock.patch.object(ModularRealmAuthorizer, 'check_role') as mra_cr:
        dsm.check_role('identifiers', 'permission_s')
        mra_cr.assert_called_once_with('identifiers', 'permission_s')

def test_dsm_start(
        default_security_manager, mock_default_session_manager, monkeypatch):
    """
    unit tested:  start

    test case:
    passes request on to session manager 
    """
    dsm = default_security_manager
    mdsm = mock_default_session_manager
    monkeypatch.setattr(dsm, 'session_manager', mdsm)
    with mock.patch.object(MockDefaultSessionManager, 'start') as mdsm_start:
        mdsm_start.return_value = None
        dsm.start('session_context')
        mdsm_start.assert_called_once_with('session_context')

def test_dsm_get_session(
        default_security_manager, mock_default_session_manager, monkeypatch):
    """
    unit tested:  get_session

    test case:
    passes request on to session manager 
    """
    dsm = default_security_manager
    mdsm = mock_default_session_manager
    monkeypatch.setattr(dsm, 'session_manager', mdsm)
    with mock.patch.object(MockDefaultSessionManager, 'get_session') as mdsm_gs:
        mdsm_gs.return_value = None
        dsm.get_session('sessionkey123')
        mdsm_gs.assert_called_once_with('sessionkey123')


def test_dsm_create_subject_context(
        default_security_manager, mock_default_session_manager, monkeypatch):
    """
    unit tested:  create_subject_context

    test case:  
    returns a new DefaultSubjectContext instance
    """
    dsm = default_security_manager
    result = dsm.create_subject_context()
    assert isinstance(result, DefaultSubjectContext)

def test_dsm_create_subject_wo_context(default_security_manager):
    """
    unit tested:  create_subject

    test case:
    When no subject_context argument is given, a new subject_context is 
    created.  The subject_context is used to create a new subject, which is 
    saved and then returned.
    """
    dsm = default_security_manager

    testcontext = DefaultSubjectContext()
    testcontext.authenticated = True
    testcontext.authentication_token = 'dumb_token'
    testcontext.account = 'dumb_account'
    testcontext.subject = 'existing_subject'

    with mock.patch.object(dsm, 'ensure_security_manager') as dsm_esm:
        dsm_esm.return_value = testcontext 
        with mock.patch.object(dsm, 'resolve_session') as dsm_rs:
            dsm_rs.return_value = testcontext 
            with mock.patch.object(dsm, 'resolve_identifiers') as dsm_rp:
                dsm_rp.return_value = testcontext 
                with mock.patch.object(dsm, 'do_create_subject') as dsm_dcs:
                    dsm_dcs.return_value = 'subject' 
                    with mock.patch.object(dsm, 'save') as dsm_save:
                        dsm_save.return_value = None

                        result = dsm.create_subject(authc_token='dumb_token', 
                                                    account='dumb_account',
                                                    existing_subject='existing_subject')
                        
                        dsm_esm.assert_called_once_with(testcontext)
                        dsm_rs.assert_called_once_with(testcontext)
                        dsm_rp.assert_called_once_with(testcontext)
                        dsm_dcs.assert_called_once_with(testcontext)
                        assert result == 'subject'

def test_dsm_create_subject_w_context(default_security_manager):
    """
    unit tested:  create_subject

    test case:
    context is passed as an argument, and so it is used
    """
    dsm = default_security_manager

    testcontext = DefaultSubjectContext()
    testcontext.authenticated = True
    testcontext.authentication_token = 'dumb_token'
    testcontext.account = 'dumb_account'
    testcontext.subject = 'existing_subject'

    with mock.patch.object(dsm, 'ensure_security_manager') as dsm_esm:
        dsm_esm.return_value = testcontext 
        with mock.patch.object(dsm, 'resolve_session') as dsm_rs:
            dsm_rs.return_value = testcontext 
            with mock.patch.object(dsm, 'resolve_identifiers') as dsm_rp:
                dsm_rp.return_value = testcontext 
                with mock.patch.object(dsm, 'do_create_subject') as dsm_dcs:
                    dsm_dcs.return_value = None 
                    with mock.patch.object(dsm, 'save') as dsm_save:
                        dsm_save.return_value = None

                        dsm.create_subject(subject_context=testcontext)
                        
                        dsm_esm.assert_called_once_with(testcontext)
                        dsm_rs.assert_called_once_with(testcontext)
                        dsm_rp.assert_called_once_with(testcontext)
                        dsm_dcs.assert_called_once_with(testcontext)


def test_dsm_rememberme_successful_login(
        default_security_manager, mock_remember_me_manager, monkeypatch):
    """
    unit tested:  remember_me_successful_login

    test case:
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'remember_me_manager', mock_remember_me_manager)

    with mock.patch.object(MockRememberMeManager,
                           'on_successful_login') as mrmm_osl:
        mrmm_osl.return_value = None
        dsm.remember_me_successful_login('authc_token', 'account', 'subject')
        mrmm_osl.assert_called_once_with('subject', 'authc_token', 'account')

def test_dsm_rememberme_successful_login_rmm_set_but_raises(
        capsys, default_security_manager, mock_remember_me_manager, 
        monkeypatch):
    """
    unit tested:  remember_me_successful_login

    test case:
    1) the remember_me_manager attribute is set
    2) the call for rmm.on_successful_login raises an exception
    3) a warning message is emitted
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'remember_me_manager', mock_remember_me_manager)

    with mock.patch.object(MockRememberMeManager,
                           'on_successful_login') as mrmm_osl:
        mrmm_osl.side_effect = Exception
        dsm.remember_me_successful_login('authc_token', 'account', 'subject')
        out, err = capsys.readouterr()
        assert 'threw an exception' in out 


def test_dsm_rememberme_successful_login_rmm_notset(
        capsys, default_security_manager):
    """
    unit tested:  remember_me_successful_login

    test case:
    when the remember_me_manager attribute is not set, a warning message is 
    emitted
    """
    dsm = default_security_manager
    dsm.remember_me_successful_login('authc_token', 'account', 'subject')
    out, err = capsys.readouterr()
    assert 'does not have' in out 

def test_dsm_rememberme_failed_login(
        default_security_manager, mock_remember_me_manager, monkeypatch):
    """
    unit tested:  remember_me_failed_login

    test case:
    when a remember_me_manager is set, it's on_failed_login is called
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'remember_me_manager', mock_remember_me_manager)

    with mock.patch.object(MockRememberMeManager,
                           'on_failed_login') as mrmm_ofl:
        mrmm_ofl.return_value = None
        dsm.remember_me_failed_login('authc_token', 'authc_exc', 'subject')
        mrmm_ofl.assert_called_once_with('subject', 'authc_token', 'authc_exc')


def test_dsm_rememberme_failed_login_warned(
        default_security_manager, mock_remember_me_manager, monkeypatch,
        capsys):
    """
    unit tested:  remember_me_failed_login

    test case:
    when the remember_me_manager attribute is not set, a warning message is 
    emitted
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'remember_me_manager', mock_remember_me_manager)

    with mock.patch.object(MockRememberMeManager,
                           'on_failed_login') as mrmm_ofl:
        mrmm_ofl.side_effect = Exception
        dsm.remember_me_failed_login('authc_token', 'authc_exc', 'subject')
        out, err = capsys.readouterr()
        assert 'threw an exception' in out 

def test_dsm_rememberme_logout(
        default_security_manager, mock_remember_me_manager, monkeypatch):
    """
    unit tested:  remember_me_logout

    test case:
    when a remember_me_manager is set, it's on_logout is called
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'remember_me_manager', mock_remember_me_manager)

    with mock.patch.object(MockRememberMeManager,
                           'on_logout') as mrmm_ol:
        mrmm_ol.return_value = None
        dsm.remember_me_logout('subject')
        mrmm_ol.assert_called_once_with('subject')

def test_dsm_rememberme_logout_warned(
        default_security_manager, mock_remember_me_manager, monkeypatch, 
        capsys):
    """
    unit tested:  remember_me_logout

    test case:
    prints a warning when remember_me_manager raises an exception
    """
    dsm = default_security_manager
    monkeypatch.setattr(dsm, 'remember_me_manager', mock_remember_me_manager)

    class MockSubject:
        def __init__(self):
            self.identifiers = {'username': 'username'}

    with mock.patch.object(MockRememberMeManager,
                           'on_logout') as mrmm_ol:
        mrmm_ol.side_effect = Exception
        dsm.remember_me_logout(MockSubject())
        out, err = capsys.readouterr()
        assert 'threw an exception during on_logout' in out 

def test_dsm_login_success
    """
    unit tested:  login

    test case:
        authenticate_account returns an account, create_subject is called,
        on_successful_login is called, and then logged_in is returned
    """

#def test_dsm_login_raises_then_succeeds
    """
    unit tested:  login

    test case:
    authenticate_account raises an AuthenticationException, on_failed_login
    succeeds, and an AuthenticationException is raised up the stack
    """

#def test_dsm_login_raises_then_raises
    """
    unit tested:  login

    test case:
    authenticate_account raises an AuthenticationException, on_failed_login
    raises, a warning is emitted, and an AuthenticationException is raised up 
    the stack
    """

#def test_on_successful_login
    """
    unit tested:  on_successful_login

    test case:
    passes call on to remember_me_successful_login
    """

#def test_onfailed_login
    """
    unit tested:  on_failed_login

    test case:
    passes call on to remember_me_failed_login
    """

#def test_before_logout
    """
    unit tested:  before_logout 

    test case:
    passes call on to remember_me_logout
    """

#def test_copy
    """
    unit tested:  copy

    test case:
    returns a new DefaultSubjectContext
    """

#def test_do_create_subject
    """
    unit tested:  do_create_subject

    test case:
    passes call onto subject_factory.create_subject
    """

#def test_save
    """
    unit tested:  save

    test case:
    passes call onto subject_store.save
    """

#def test_delete
    """
    unit tested:  delete 

    test case:
    passes call onto subject_store.delete
    """

#def ensure_security_manager_resolves
    """
    unit tested:  ensure_security_manager

    test case:
    resolve_security_manager returns the subject_context
    """

#def ensure_security_manager_doesntresolve
    """
    unit tested:  ensure_security_manager

    test case:
    resolve_security_manager returns None, and then ensure_security_manager
    returns a subject_context whose security_manager is the dsm
    """

