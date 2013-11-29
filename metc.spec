%global __jar_repack %{nil}
%global debug_package %{nil}

%global homedir   %{_datadir}/%{name}
%global logdir    %{_localstatedir}/log/%{name}
%global rundir    %{_localstatedir}/run/%{name}

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

BuildArch:     noarch

%description
Marketcetera Automated Trading Platform

%prep
%setup -q

%build
mvn package

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{homedir}
mkdir -p %{buildroot}%{homedir}/lib
cp -pa target/classes/* %{buildroot}%{homedir}

for jar in `find target/repo -name *.jar`; do
  cp $jar %{buildroot}%{homedir}/lib
done

mkdir -p %{buildroot}/var/run/ors
mkdir -p %{buildroot}/var/log/ors

ln -s %{homedir}/bin/ors_install_inst %{buildroot}%{_bindir}
ln -s %{homedir}/bin/sa_install_inst %{buildroot}%{_bindir}
ln -s %{homedir}/ors/bin/orsctl %{buildroot}%{_bindir}
ln -s %{homedir}/ors/bin/ors %{buildroot}%{_bindir}
ln -s %{homedir}/strategyagent/bin/strategyagent %{buildroot}%{_bindir}
ln -s %{homedir}/strategyagent/bin/sactl %{buildroot}%{_bindir}
ln -s %{homedir}/orderloader/bin/orderloader %{buildroot}%{_bindir}

%post
#%{_bindir}/ors_install_inst --destdir %{homedir}/default_inst --rundir %{rundir} --logdir %{logdir}

%files
%attr(-,root,root)
%{_bindir}/ors_install_inst
%{_bindir}/sa_install_inst
%{_bindir}/ors
%{_bindir}/orsctl
%{_bindir}/strategyagent
%{_bindir}/sactl
%{_bindir}/orderloader

%{homedir}

%changelog
* Mon Aug 05 2013 Alex Lee <lu.lee05@gmail.com> 2.2.0-1
- new package

