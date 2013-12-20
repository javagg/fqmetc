%global __jar_repack %{nil}
%global debug_package %{nil}

%global homedir   %{_datadir}/%{name}
%global logdir    %{_localstatedir}/log/%{name}
%global rundir    %{_localstatedir}/run/%{name}

%if 0%{?fedora} >= 16 || 0%{?rhel} >= 7
  %global with_systemd 1
%else
  %global with_systemd 0
%endif

Summary:       Marketcetera Automated Trading Platform
Name:          marketcetera
Version:       2.2.0
Release:       1%{?dist}
Group:         Applications/Internet
License:       GPLv3
URL:           http://www.marketcetera.org
Source0:       %{name}-%{version}.tar.gz

Requires:      java-1.7.0-openjdk
Requires:      java-1.7.0-openjdk-devel
BuildRequires: jpackage-utils
%if 0%{?fedora} >= 19
BuildRequires: maven
%endif
%if 0%{?rhel} >= 6
BuildRequires: maven3
%endif

Requires:      %{name}-common = %{version}-%{release}
BuildArch:     noarch

%description
Marketcetera Automated Trading Platform

%package common
Summary:       Common files for %{name}
Group:         Applications/Internet
Requires:      %{name}-common = %{version}-%{release}
BuildArch:     noarch
%description common
This package contains the file shard between the subpackages of %{name}.

%package ors
Summary:       ORS server of %{name}
Group:         Applications/Internet
Requires:      %{name}-common = %{version}-%{release}
BuildArch:     noarch
%description ors
This package contains the ORS server of %{name}

%package strategyagent
Summary:       Strategy Agent of %{name}
Group:         Applications/Internet
Requires:      %{name}-common = %{version}-%{release}
BuildArch:     noarch
%description strategyagent
This package contains the strategy agent of %{name}

%package orderloader
Summary:       Order Loader of %{name}
Group:         Applications/Internet
Requires:      %{name}-common = %{version}-%{release}
BuildArch:     noarch
%description orderloader
This package contains the order loader of %{name}

%prep
%setup -q

%build
mvn package

%install
#sed -i -e '/<value>stomp:\/\/${metc.ws.host}:61613<\/value>/d' $orsdir/conf/messaging/broker.xml

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{homedir}/lib
cp -pa target/classes/* %{buildroot}%{homedir}
# The ors-${version}.jar in this folder is not what we need
rm -rf target/repo/net/freequant

rm %{buildroot}%{homedir}/bin/ors_install_inst

for jar in `find target/repo -name *.jar`; do
  cp $jar %{buildroot}%{homedir}/lib
done

mkdir -p %{buildroot}/var/run/ors
mkdir -p %{buildroot}/var/log/ors

mkdir -p %{buildroot}/var/run/strategyagent
mkdir -p %{buildroot}/var/log/strategyagent

ln -s %{homedir}/bin/sa_install_inst %{buildroot}%{_bindir}
ln -s %{homedir}/ors/bin/orsctl %{buildroot}%{_bindir}
ln -s %{homedir}/ors/bin/ors %{buildroot}%{_bindir}
ln -s %{homedir}/strategyagent/bin/strategyagent %{buildroot}%{_bindir}
ln -s %{homedir}/strategyagent/bin/sactl %{buildroot}%{_bindir}
ln -s %{homedir}/strategyagent/bin/sactl2 %{buildroot}%{_bindir}
ln -s %{homedir}/orderloader/bin/orderloader %{buildroot}%{_bindir}

# link strategy modules dir to lib
pushd %{buildroot}%{homedir}/strategyagent/modules
ln -s %{homedir}/lib jars
popd

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
install -D -p -m 644 ors.conf %{buildroot}%{_sysconfdir}/%{name}
%if %{with_systemd}
mkdir -p %{buildroot}%{_unitdir}
install -D -p -m 644 ors.service %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_initddir}
install -D -p -m 755 %{buildroot}%{homedir}/ors/bin/orsctl %{buildroot}%{_initddir}/ors
%endif

# Fix ors log4j configuration inplace
sed -i -e 's/^log4j.appender.file.File=.*$/log4j.appender.file.File=\/var\/log\/ors\/ors.log/' %{buildroot}%{homedir}/ors/conf/log4j/server.properties

#install -D -p -m 644 ors.logrotate.d %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%post ors
%if %{with_systemd}
  /bin/systemctl --system daemon-reload
%else
  /sbin/chkconfig --add ors || :
%endif

%preun ors
if [ "$1" -eq "0" ]; then
%if %{with_systemd}
  /bin/systemctl --no-reload disable ors.service
%else
  /sbin/chkconfig --del ors || :
%endif
fi

%files common
%attr(-,root,root)

%{homedir}/lib
%{homedir}/sql

%files ors
%attr(-,root,root)
%attr(0755,-,-) %{_bindir}/ors
%attr(0755,-,-) %{_bindir}/orsctl
%attr(0755,-,-) %{homedir}/ors/bin/*
%{homedir}/ors
/var/run/ors
/var/log/ors

%attr(0644,-,-) %{_sysconfdir}/%{name}/ors.conf
%if %{with_systemd}
%attr(0644,-,-) %{_unitdir}/ors.service
%else
%attr(0755,-,-) %{_initddir}/ors
%endif
#%attr(0644,-,-) %{_sysconfdir}/logrotate.d/ors

%files strategyagent
%attr(-,root,root)
%attr(0755,-,-) %{_bindir}/sa_install_inst
%attr(0755,-,-) %{_bindir}/strategyagent
%attr(0755,-,-) %{_bindir}/sactl
%attr(0755,-,-) %{_bindir}/sactl2
%attr(0755,-,-) %{homedir}/strategyagent/bin/*
%{homedir}/strategyagent
%attr(0755,-,-) %{homedir}/bin/sa_install_inst
/var/run/strategyagent
/var/log/strategyagent

%files orderloader
%attr(-,root,root)
%attr(0755,-,-) %{_bindir}/orderloader
%{homedir}/orderloader

%changelog
* Mon Aug 05 2013 Alex Lee <lu.lee05@gmail.com> 2.2.0-1
- new package

