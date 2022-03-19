#
# Conditional build:
%bcond_without	prof	# profiling library
#
%define		pkgname	hxt
Summary:	A collection of tools for processing XML with Haskell
Name:		ghc-%{pkgname}
Version:	9.3.1.18
Release:	2
License:	MIT
Group:		Development/Languages
#Source0Download: http://hackage.haskell.org/package/hxt
Source0:	http://hackage.haskell.org/package/%{pkgname}-%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	fc58dede9d9df529486d91d015bfec63
URL:		http://hackage.haskell.org/package/hxt
BuildRequires:	ghc >= 6.12.3
BuildRequires:	ghc-hxt-charproperties >= 9.1
BuildRequires:	ghc-hxt-regex-xmlschema >= 9.2
BuildRequires:	ghc-hxt-unicode >= 9.0.1
BuildRequires:	ghc-network >= 2.4
BuildRequires:	ghc-network-uri >= 2.6
%if %{with prof}
BuildRequires:	ghc-prof
BuildRequires:	ghc-hxt-charproperties-prof >= 9.1
BuildRequires:	ghc-hxt-regex-xmlschema-prof >= 9.2
BuildRequires:	ghc-hxt-unicode-prof >= 9.0.1
BuildRequires:	ghc-network-prof >= 2.4
BuildRequires:	ghc-network-uri-prof >= 2.6
%endif
BuildRequires:	rpmbuild(macros) >= 1.608
%requires_eq	ghc
Requires(post,postun):	/usr/bin/ghc-pkg
Requires:	ghc-hxt-charproperties >= 9.1
Requires:	ghc-hxt-regex-xmlschema >= 9.2
Requires:	ghc-hxt-unicode >= 9.0.1
Requires:	ghc-network >= 2.4
Requires:	ghc-network-uri >= 2.6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debuginfo is not useful for ghc
%define		_enable_debug_packages	0

# don't compress haddock files
%define		_noautocompressdoc	*.haddock

%description
The Haskell XML Toolbox bases on the ideas of HaXml and HXML, but
introduces a more general approach for processing XML with Haskell.
The Haskell XML Toolbox uses a generic data model for representing XML
documents, including the DTD subset and the document subset, in
Haskell. It contains a validating XML parser, a HTML parser, namespace
support, an XPath expression evaluator, an XSLT library, a RelaxNG
schema validator and funtions for serialization and deserialization
of user defined data. The library makes extensive use of the arrow
approach for processing XML.

%package prof
Summary:	Profiling %{pkgname} library for GHC
Summary(pl.UTF-8):	Biblioteka profilująca %{pkgname} dla GHC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	ghc-hxt-charproperties-prof >= 9.1
Requires:	ghc-hxt-regex-xmlschema-prof >= 9.2
Requires:	ghc-hxt-unicode-prof >= 9.0.1
Requires:	ghc-network-prof >= 2.4
Requires:	ghc-network-uri-prof >= 2.6

%description prof
Profiling %{pkgname} library for GHC.  Should be installed when
GHC's profiling subsystem is needed.

%description prof -l pl.UTF-8
Biblioteka profilująca %{pkgname} dla GHC. Powinna być zainstalowana
kiedy potrzebujemy systemu profilującego z GHC.

%prep
%setup -q -n %{pkgname}-%{version}

%build
runhaskell Setup.lhs configure -v2 \
	%{?with_prof:--enable-library-profiling} \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--docdir=%{_docdir}/%{name}-%{version}

runhaskell Setup.lhs build
runhaskell Setup.lhs haddock --executables

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d

runhaskell Setup.lhs copy --destdir=$RPM_BUILD_ROOT

# work around automatic haddock docs installation
%{__rm} -rf %{name}-%{version}-doc
cp -a $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} %{name}-%{version}-doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

runhaskell Setup.lhs register \
	--gen-pkg-config=$RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf

find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -type d | %{__sed} "s|$RPM_BUILD_ROOT|%dir |" > %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.hi' | %{__sed} "s|$RPM_BUILD_ROOT||" >> %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.dyn_hi' | %{__sed} "s|$RPM_BUILD_ROOT||" >> %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.p_hi' | %{__sed} "s|$RPM_BUILD_ROOT||" > %{name}-prof.files

%clean
rm -rf $RPM_BUILD_ROOT

%post
%ghc_pkg_recache

%postun
%ghc_pkg_recache

%files -f %{name}.files
%defattr(644,root,root,755)
%doc %{name}-%{version}-doc/*
%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*.so
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*.a
%exclude %{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*_p.a

%if %{with prof}
%files prof -f %{name}-prof.files
%defattr(644,root,root,755)
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*_p.a
%endif
