-- Pre migration task second step:
-- Create database functions and stored procedures to help with the data transformation from DB2 to PostgreSQL.
-- 1. Create functions to help transfrom submitting party names.
-- 2. Create functions to help transform addresses.
-- 3. Create functions to extract fractional ownership interest numerators and denominators from legacy interest text.
-- 4. Create function to extract mhr_descriptions.make and mhr_descriptions.model from legacy descript.makemodl.
-- 5. Create functions to insert registrations into mhr_* tables from staging tables.

--
-- Try to parse the legacy descript.makemodl into make and model.
--
create or replace function public.mhr_conversion_make_model(v_text character varying, v_make boolean) returns character varying
  immutable
  language plpgsql
as $$
declare
  -- order is important within the array for replacing
  make_1 text[] := '{"EXCELLENCE","ENGINEERED","EMPEROR","EMBASY","ELMONTE","EL MONTE","EDINBURGH","EARL GREY","DUCHESS","DREAM HOME","DREAMHOME"' ||
                   ',"CROWNPOINTE","CROWNPOINT","COVINGTON","COUNTRYLAND","COUNTRY","CONTINENTAL","DELUXE","DESIGN 5","DOUGLAS"' ||
                   ',"CONESTOGA","COMMODORE","COLWOOD","COLUMBIAN","COLUMBIA","COLONY","COLONOY","COLLINGWOOD","COACH","CHIMO","GALAXY SERIES"' ||
                   ',"CHICKASHA","CHANCELLOR","CHANCELLER","CHANCELER","CHAMPION","CHALLENGER","CAVCO","CASTLEWOOD","CASA","CAN-AMERA"' ||
                   ',"CANTERBURY","CAN AMERA","CANAMARA","CANADIANA","CANADIAN","CAMPMOBILE","BUNGALO","BUDDY","BROOKWOOD","BROOKSWOOD"' ||
                   ',"BROOKDALE","BROCKWOOD","BROADMORE","BROADMOOR","BRIARWOOD","BREWSTER","BON PRIX","BONNEVILLE","BONA VISTA","BONAVISTA"' ||
                   ',"BOISE","BIRKSHIRE","BEL-AIR","ATCO","ASPIRE","AMERICIAN","AMBASSADOR","FOUR SEASONS","CHINOOK","LEADER"' ||
                   ',"SOMERVILLE","BRITANNY","SCHULTZ","CENTURY","MONTEGO","CIMMERON","MILLENNIUM","HAMPTON","KEYSTONE","CHEHALIS"' ||
                   ',"WINTERSUN","SUMMERSUN","PINNACLE","LIMITED","TOWNHOUSE","PLAYERS","PLAYER","CUSTOM","SOUTHWOOD","VELMONT"' ||
                   ',"SECURITY","TOWN ' || chr(38) || ' COUNTRY","VAGABOND","GLENDALL","BUILDER","MERRIMAN","SILVERWOOD","DIPLOMAT","MEDALLION","BRENTWOOD"' ||
                   ',"CREST","HAWTHORNE","EXECUTIVE","GENERAL","NORWESTER","BENDIX","RESORT","ESTATE","LAKEHURST"}';
  make_2 text[] := '{"SANDPOINTE","REPUBLIC","FLEETWOOD","OAKCREST","PRESTIGE","EMBASSY","LAURENTIAN","PACIFIC PARK","DETROITER","CIKSA","CLASSIC"' ||
                   ',"CAMBRIDGE","DARTMOUTH","PREMIER","KENMORE","FRONTIER","GLENDALE","SLATER","WILD ROSE","WILDROSE","WINDRIVER"' ||
                   ',"STATESMAN","SORRENTO","DALHOUSIE","SOMMERVILLE","HIGHWOOD","CREEKSIDE","SAFEWAY","SENIOR","ALMA","ARBUTUS"' ||
                   ',"AVONLEA","CONNELY","FULLMER","SALVADOR","STOREY","LEGACY","MASTERPIECE","REGENT","MANOR","MANSURA"' ||
                   ',"BERKSHIRE","SEACREST","GIBRALTAR","MERIDIAN","MODULINE","SHELTER","MAGNUM","RIDGEWOOD","VILLA","REAL"' ||
                   ',"WIND RIVER","MIRAGE","SIERRA","LEXINGTON","ROYALE","SYMPHONY","LANDMARK","MONARCH","KNIGHT","BELMANOR"' ||
                   ',"CORNERSTONE","GENESIS","BIRCHWOOD","PARAMOUNT","MASTERPIECE","COUNTRY ESTATE","WINFIELD","JELDWYN","PROVINCIAL","FRIENDSHIP HOMES"' ||
                   ',"GLENBROOK","GLENRIVER","GOLDEN STATE","GOLD MADALLION","GREAT LAKES","HEARTHSIDE","HIGHSTYLE","HILLVIEW","HOLLY","HOMCO"' ||
                   ',"GALLAGHER LAKE","GALLAGHER LK","GALLAGHER","PACIFIC CABIN","WARREN AVENUE","WA DEVELOPMENT","CORNERTSTONE","LAKE CONTRY","WARREN AVE","WOINFIELD"' ||
                   ',"VALUECRAFT","4 SEASONS","DUTCH","ECONO","EXCELLENCY","FAIRMONT","GENDALL","GIBRALTER","GLEN ABBEY"}';
  make_3 text[] := '{"HOMEBUILT","HOME BUILT","HOMESTEAD","HUNTINGDON","IMPERIAL","INGLEWOOD","KLASSIC","KUSTOM KOACH","LAMPLIGHTER","LEISUREHOME","LOG MOBILE"' ||
                   ',"MABCO","MACKENZIE","MANCHESTER","MANSUA","MANSURE","MAPLE LEAF","MARINER","MARLETTE","MAYFAIR","MCGENNESS"' ||
                   ',"MEADOWBROOK","MEADOW BROOK","MILA","MODERN HOME","MODULAR","MONTROSE","MORROCCO","MOUNTBATTEN","NORTHWOOD","NASHUA"' ||
                   ',"NAUTICA","NEONEX","NEWCASTLE","NEW HORIZON","NOBLE","NORTHLANDER","NORTHLAND","NORTH LANDER","NORTHWESTERN","NORTHWEST"' ||
                   ',"MCGINNESS","MCGUINNES","MCGUINNESS","FOUNDATION","OLYMPIC","PACEMAKER","PACESETTER","PACIFICA","PAGE","PARKWOOD"' ||
                   ',"MCGUINESS","TEDS HOME","TRIPLE","UNITED","VALU CRAFT","VALUCRAFT","VALUE CRAFT","VELAIRE","VINTAGE","VISCOUNT"' ||
                   ',"PATHFINDER","PEMBROKE","PHASE","PONTIAC CHIEF","PYRAMID","RITZ-CRAFT","ROADCRAFT","ROLLAHOME","ROLLERHOME","ROYAL"' ||
                   ',"SEAVIEW PARK","WESTWIND","SEVILLE","SHELBY","SIENNA","SILVERSTAR","SILVER STREAK","SILVER WOOD","SKYLINE","SOLARNO"' ||
                   ',"SOMMERSUN","SOMERSET","SPACEMASTER","SPANISH","SPRINGER","SQUIRE","CHATEAU","SUMMER SUN","SUNBOW","TRADITIONAL"' ||
                   ',"WELDWOOD","WESTBROOK","WESTCOAST","WESTERNER","WESTMINSTER","WIMBLEDON","WINALTA","WINDSOR","WINFIED","WINTER SUN","WNFIELD"' ||
                   ',"NORTHWEST SPECIAL","NORTHWOOD","NOR WESTERN","NOR''WESTERN","NOR-WESTER","NIAGARA","TED''S HOME","TRADITION","TRIPLE E","SRI"}';
  make_4 text[] := '{"COULTER","SHETIR","1ST EDITION","SUNTERRA","ULTRA","WINDIELD","WOLFE CREEK","HIGH POINTE","WINFFIELD","WONFIELD","WIINFIELD"' ||
                   ',"PACIFIC GRANDE","WINDIELD","WINFELD","WINFILED","BRETTON","WINFIIELD","BRIDGEWATER","COTTAGE","LAKEHOUSE","BW DEVELOPMENT"' ||
                   ',"BW DOUBLE","WINFIEELD","WINFIEKD","WINFIELLD","KELOWNA","MGANUM PLUS","SYPMPHONY","DESTINATION","DESERTWOODS","ACADIAN"' ||
                   ',"ACAIDIAN","ADDISON","AMBER RIDGE","ARILINGTON","ARLINGTON","AURORA","AUSTIN","BARRINGTON","BAY SPRINGS","BRITTANNY"' ||
                   ',"EXPLORER","FISHERY","FPI","FREIGHT SAVER","FREIGHTSAVER","FUQUA","GLENGARRY","GOLDEN WEST","GRAYSON","HERRITAGE"' ||
                   ',"HIDE AWAY","HIGHVIEW","INTREPID","ISLAND WEST INDUSTRIES","IWI","KIMBERLY","KITSILANO","LAKESHIRE","LAKEWOOD","MADISON"' ||
                   ',"MAGMUM PLUS","MAJESTIC","MANHATTAN","MANSORA","MAPLE RIDGE","MAPLE WOOD","MAPLEWOOD","MASTERPEICE","MASTERPRIECE","METROPOLITAN"' ||
                   ',"MIDLAND","MONTEREY","MOUNTAIN","NORMANDY","PALM HARBOR","PRINCETON","PRIVATE LABEL","RANCHLAND","REGAL","ROCKY MOUNTAIN"' ||
                   ',"SAN JUAN","SEABREEZE","SHERWOOD","SHOWHOME","SPRUCE RIDGE","STAMPEDE","TEAK WOOD","TEDSHOME","TIMBER RIDGE","TITAN"' ||
                   ',"TORINO","TRIUMPH","TUDOR","VALMONT","VOYAGEUR","WALNUT GROVE","WIFIELD"' ||
                   ',"CAPE COD","SAVILLE","CJ SERIES","CROWNE POINT","MARQUIS","YUKON","EXPLORER","DAWSON","DEVONIAN","EMERALD","EMPIRE"}';
  make_5 text[] := '{"ELMA","EMPRESS","FIRST EDITION","NORTHERN","MANSION","HARALEX","CONCORDE","ELCAR","AQUARIUS","ADMIRAL","ALCAR"' ||
                   ',"AMBASADOR","AMBASSODOR","AMBBASADOR","AMERICAN","AQUARIOUS","ARISTOCRAT","ART CRAFT","BELLA VISTA","BELMONT","BENDEX"' ||
                   ',"BERDICK","BILTMORE","BRIERWOOD","BRITANY","BRITTANY","BROADMOR","BROAD MORE","BUCKINGHAM","BUILTMORE","BUILTRIGHT"' ||
                   ',"BUILT-RITE","CAMEO","CAN/AMERA","CANAMERA","CAPEWOOD","CARAVELLE","CHALET","CHANESLOR","CHANLELLOR","COMMADORE"' ||
                   ',"COMODORE","COMPANION","COSMOPOLITAN","DREAM-HOME","DREAMHOUSE","ESTA VISTA","EVERGREEN","FLASHBACK","FLEET WOOD","FOUR SEASON"' ||
                   ',"GARDNER","GENTRY","GLEN BROOK","GLENDETTE","GLENHAVEN","GLEN HAVEN","GLEN RIVER","GOLDEN SLATE","GOLDEN ZEPHYR","GUARDIAN"' ||
                   ',"HARALEUX","HARALEX","HERITAGE","HIGHLANDER","HIGH WOOD","HOLIDAY","JUPITER","KENSKILL","KENTWOOD","KINGSWAY"' ||
                   ',"KORONET","LAKE VIEW","LAMPLITER","LAMPLITTER","MACGINNIS","MARSHFIELD","MASTERCRAFT","MAYFLOWER","MCGINNISS","MCGUINNISS"' ||
                   ',"NOBEL","NORTHBROOK","NORTH WEST","NORWEST","OLYMPIAN","OLYMPIA","PARAMONT","PARKETTE","POLAR","RICHARDSON"' ||
                   ',"ROLLOHOME","SANDPOINT","SHAMROCK","SIGNATURE","STYLE CRAFT","SUNLITE","TAMARACK","TEDS'' HOME","VAN DYKE","VELAIR"' ||
                   ',"CROWN POINTE","EDXECUTIVE","EXEUTIVE","GEMINI","INTERNATIONAL","MARSH FIELD","PACE MAKER","SHETLER","SOMMERSET","SUN ISLE"' ||
                   ',"MELODY","MICHIGAN","MONTCLAIR","MONTE ROSE","MONT ROSE","MOUNTROSE","MUTTART","NEW MOON","NEW YORKER"}';

  make_6 text[] := '{"TERRACRUISER","ACCENT","BALMORAL","BON-PRIX","BOWES PORTAGER","BUCCANEER","EMPORER","JUPITAR","LIBERTY","LEISURE","MANCO"' ||
                   ',"BRITTANI","CHEYENNE","COMMADOR","CONCORD","ELGIN","ELMONTY","EMPOROR","ESTAVILLE","GLENWOOD","HALLMARK"' ||
                   ',"HENSLEE","ISPEN","NORFAB","NOR'' WESTERN","OVERLANDER","PARKLANE","REVERE","RICO","COMMONWEALTH","ROYCRAFT"' ||
                   ',"SOLANO","STATESMEN","SUBURBAN","WESTWOOD","HIGHLAND PARK","HOMECO","LETHBRIDGE","MCLURE","TED''S","VELARIE","VELLAIRE"' ||
                   ',"ELITE","DELTA","WESTERN","EXPANDO","EMBASSADOR","ANDERSON","ARVADA","CAN AMERICA","OAK PARK","DELTA","DESIGN ''5''"' ||
                   ',"DETROIT","DIPLIMATE","EAGLE","FAIRVIEW","HOLIDAIRE","LIFESTYLE","MAGNOLIA","NW SPECIAL","OAKHURST","PEERLESS"' ||
                   ',"SAHARA","SCHULT","SILVER","STATIER","SUMMIT","TEDS","TOWNEHOUSE","TRENDSETTER","VICTOR","NOVA"' ||
                   ',"CANDLEWOOD","RESIDENTIAL","CHADWICK","COLONIAL","CATALINA","ARBOR","AVALON","CARAVAN","CHEMAINUS","GRANDEUR","REGENCY"' ||
                   ',"RESIDENTIAL","SPECTRA","ZEPHYR","KINGSWOOD","PINEWOOD","DARTHMOUTH","BAINBRIDGE","CAMBIRDGE","FESTIVAL"' ||
                   ',"HIGHWAY PARK","HIWOOD","IMAGE 2000","LEGEND","LENNOX","MCGINNIS","MONOGRAM","OAKCREAST","VOLAIRE","URBAN","VENUS"' ||
                   ',"GILBRALTAR","SHILO","DARMOUTH","DRATMOUTH","ALEXANDERIA","ASCOT","ASHCROFT","BENTLEY","BONIVISTA","VEGAS", "CHELSEA"' ||
                   ',"CORNERSTON","ADVENT","AFFINITY","SPRINGS","GALAXY"' ||
                   ',"PAIGE","REMBRANDT","REX","STATEMAN","TEDS-HOME","VARDO","VEL AIRE","VELMOUNT","VENTURA","ATWOOD","BELAIRE","BLAIR", "WINFIEL"}';
  v_result varchar(60);
begin
  -- Empty value do nothing.
  if v_text is null or v_text = '' then
    return null;
  end if;
  v_result := null;
  for i in 1 .. array_upper(make_1, 1)
  loop
    if v_text LIKE make_1[i] || ' %' then
      if v_make then
        v_result := make_1[i];
      else
        v_result := TRIM(REPLACE(v_text, make_1[i], ''));
      end if;
    end if;
  end loop;
  if v_result is null then
    for i in 1 .. array_upper(make_2, 1)
    loop
      if v_text LIKE make_2[i] || ' %' then
        if v_make then
          v_result := make_2[i];
        else
          v_result := TRIM(REPLACE(v_text, make_2[i], ''));
        end if;
      end if;
    end loop;
  end if;

  if v_result is null then  
    for i in 1 .. array_upper(make_3, 1)
    loop
      if v_text LIKE make_3[i] || ' %' then
        if v_make then
          v_result := make_3[i];
        else
          v_result := TRIM(REPLACE(v_text, make_3[i], ''));
        end if;
      end if;
    end loop;
  end if;
  
  if v_result is null then
    for i in 1 .. array_upper(make_4, 1)
    loop
      if v_text LIKE make_4[i] || ' %' then
        if v_make then
          v_result := make_4[i];
        else
          v_result := TRIM(REPLACE(v_text, make_4[i], ''));
        end if;
      end if;
    end loop;
  end if;
  
  if v_result is null then
    for i in 1 .. array_upper(make_5, 1)
    loop
      if v_text LIKE make_5[i] || ' %' then
        if v_make then
          v_result := make_5[i];
        else
          v_result := TRIM(REPLACE(v_text, make_5[i], ''));
        end if;
      end if;
    end loop;
  end if;
  
  if v_result is null then
    for i in 1 .. array_upper(make_6, 1)
    loop
      if v_text LIKE make_6[i] || ' %' then
        if v_make then
          v_result := make_6[i];
        else
          v_result := TRIM(REPLACE(v_text, make_6[i], ''));
        end if;
      end if;
    end loop;
  end if;

  if v_result is not null then
    if not v_make then
      -- v_result := TRIM(REPLACE(v_text, v_result, ''));
      v_result := TRIM(REPLACE(v_result, '/', ' '));
    end if;
    return v_result;
  elsif v_make and position(left(v_text, 1) in '#1234567890') < 1 and left(v_text, 5) != 'MODEL' and left(v_text, 4) != 'MOD.' then
    return v_text;  
  elsif not v_make and (left(v_text, 5) = 'MODEL' or left(v_text, 4) = 'MOD.') then
    return v_text;
  elsif not v_make and position(left(v_text, 1) in '#1234567890') > 0 then
    return v_text;
  end if;
  
  return null;
end;
$$;

--
-- Extract the owner group fractional interest numerator or denominator as an integer from the interest text.
--
create or replace function public.mhr_conversion_interest_fraction(v_interest character varying, v_numerator boolean) returns integer
  immutable
  language plpgsql
as $$
declare
  v_result integer := 0;
  v_text VARCHAR(40);
  v_split VARCHAR(20) := '';
begin
  -- Empty value do nothing.
  if v_interest is null or length(v_interest) < 3 then
    return null;
  elsif POSITION('AN UNIDIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'AN UNIDIVIDED', ''));
  elsif POSITION('AN UNDIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'AN UNDIVIDED', ''));
  elsif POSITION('UNDIVEDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVEDED', ''));
  elsif POSITION('UNDIVIVED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIVED', ''));
  elsif POSITION('UNDIVIDIED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIDIED', ''));
  elsif POSITION('UNDIVIEDE' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIEDE', ''));
  elsif POSITION('UNDIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIDED', ''));
  elsif POSITION('UNDIVIDEC' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIDEC', ''));
  elsif POSITION('UNDIVED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVED', ''));
  elsif POSITION('UNDVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDVIDED', ''));
  elsif POSITION('UNIDIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNIDIVIDED', ''));
  elsif POSITION('UNDIVIED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIED', ''));
  elsif POSITION('UNDIVIDIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIDIDED', ''));
  elsif POSITION('INDIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'INDIVIDED', ''));
  elsif POSITION('UNDIVIDE' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVIDE', ''));
  elsif POSITION('UNIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNIVIDED', ''));
  elsif POSITION('UDIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UDIVIDED', ''));
  elsif POSITION('UN DIVIDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UN DIVIDED', ''));
  elsif POSITION('UNDIVDED' in v_interest) > 0 then
    v_text := TRIM(REPLACE(v_interest, 'UNDIVDED', ''));
  else
    v_text := v_interest;
  end if;
  if POSITION('TH INTEREST' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'TH INTEREST', ''));
  elsif POSITION('INTEREST' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'INTEREST', ''));
  elsif POSITION('INT.' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'INT.', ''));
  end if;

  if POSITION('THS' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'THS', ''));
  elsif POSITION('TH' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'TH', ''));
  end if;

  if POSITION('AS TO A' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'AS TO A', ''));
  elsif POSITION('AS TO' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'AS TO', ''));
  elsif POSITION('A' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'A', ''));
  elsif POSITION('INT.' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'INT.', ''));
  elsif POSITION('THS' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, 'THS', ''));
  elsif POSITION('`' in v_text) > 0 then
    v_text := TRIM(REPLACE(v_text, '`', ''));
  elsif v_text = '49.5/100' then
    v_text := '495/1000';
  elsif v_text = '19.5/100' then
    v_text := '195/1000';
  elsif v_text = '24.59/100' then
    v_text := '2459/10000';
  elsif v_text = '34.41/100' then
    v_text := '3441/10000';
  elsif v_text = 'L/2' then
    v_text := '1/2';
  end if;
 
  if POSITION('/' in v_text) > 0 then
    if v_numerator then
      v_split := TRIM(SPLIT_PART(v_text, '/', 1));
    else
      v_split := TRIM(SPLIT_PART(v_text, '/', 2));
    end if;
    v_result := CAST (v_split AS INTEGER);
  end if;
  return v_result;
  exception
    when others then
      raise exception 'Invalid interest: %', v_interest;
end;
$$;

--
-- By default the document.name submitting party is a business. Use this function to evaluate if it is an individual.
--
create or replace function public.mhr_conversion_is_individual(v_name character varying) returns boolean
  immutable
  language plpgsql
as $$
begin
  -- Empty value or starts with a digit or single word is not considered and individual name.
  if v_name is null or v_name = '' or REGEXP_REPLACE(LEFT(v_name, 1), '[0-9]','','gi') = '' then
    return false;
  elsif SPLIT_PART(v_name, ' ', 2) = '' and POSITION(',' in v_name) < 1 then
    return false;
  -- Any name that contains these designations is not considered an individual name.
  elsif POSITION(' INC' in v_name) > 0 OR POSITION(' CORP' in v_name) > 0 OR POSITION(' COMPANY' in v_name) > 0 OR
        POSITION('LTD' in v_name) > 0 OR POSITION(' LLC' in v_name) > 0 OR POSITION(' ULC' in v_name) > 0 OR
        POSITION(' SOCIETY' in v_name) > 0 OR POSITION(' LIMITED' in v_name) > 0 OR POSITION(' FIRM' in v_name) > 0 OR
        POSITION('LLP' in v_name) > 0 OR POSITION(' CO.' in v_name) > 0 then
    return false;
  -- Any name that contains these words is not considered an individual name.
  elsif POSITION('NOTARY' in v_name) > 0 OR POSITION('PUBLIC' in v_name) > 0 OR POSITION('OFFICE' in v_name) > 0 OR
        POSITION('CHAMPION' in v_name) > 0 OR POSITION(' LAW ' in v_name) > 0 OR POSITION(' LEGAL ' in v_name) > 0 OR
        POSITION(' LAWYER' in v_name) > 0 OR POSITION('BARRISTER' in v_name) > 0 OR POSITION('REGISTR' in v_name) > 0 OR
        RIGHT(v_name, 4) = ' LAW' then
    return false;
  -- Any name that contains these words is not considered an individual name.
  elsif POSITION('SERVICES' in v_name) > 0 OR POSITION('ASSOCIATE' in v_name) > 0 OR POSITION(' HOMES' in v_name) > 0 OR
        POSITION('DWELLING' in v_name) > 0 OR POSITION('BANK OF' in v_name) > 0 OR POSITION(' HOUSING' in v_name) > 0 OR
        POSITION('TRANSPORT' in v_name) > 0 OR POSITION('MANUFACTURED' in v_name) > 0 OR POSITION('MOBILE' in v_name) > 0 OR
        POSITION('GOVERNMENT' in v_name) > 0 OR RIGHT(v_name, 5) = ' HOME' then
    return false;
  elsif POSITION('PROPERTY' in v_name) > 0 OR POSITION('PROPERTIES' in v_name) > 0 OR POSITION(' SALES' in v_name) > 0 OR
        POSITION('CREDIT UNION' in v_name) > 0 OR POSITION('REAL ESTATE' in v_name) > 0 OR POSITION('STRUCTURE' in v_name) > 0 OR
        POSITION('INDUSTR' in v_name) > 0 OR POSITION('MODULINE' in v_name) > 0 OR POSITION('CARPENTRY' in v_name) > 0 OR
        POSITION(' INDIAN' in v_name) > 0 OR POSITION(' NATION' in v_name) > 0  OR POSITION(' GROUP' in v_name) > 0 then
    return false;
  elsif POSITION(' HOME ' in v_name) > 0 OR POSITION('BC' in v_name) > 0  OR POSITION('B.C' in v_name) > 0 OR
        POSITION('AUTHORITY' in v_name) > 0 OR POSITION(' OF ' in v_name) > 0 OR POSITION('MINISTRY' in v_name) > 0 OR
        POSITION(' NISSAN' in v_name) > 0 OR POSITION(' CLINIC' in v_name) > 0 OR POSITION(' INVEST' in v_name) > 0 OR
        POSITION('ASSOCIAT' in v_name) > 0 OR POSITION(' BAILIF' in v_name) > 0 OR POSITION(' AGENT' in v_name) > 0 then
    return false;
  -- Any name that contains these characters is not considered an individual name.
  -- elsif POSITION(',' in name) > 0 OR POSITION('(' in name) > 0 OR POSITION('/' in name) > 0 then
  elsif POSITION('&' in v_name) > 0 OR POSITION(' AND ' in v_name) > 0 OR POSITION(' THE ' in v_name) > 0 then
    return false;
  else
    return true;
  end if;
end;
$$;

--
-- legacy document.name and mhomnote.name extract submitting party individual last name
--
create or replace function public.mhr_conversion_individual_last(v_name character varying) returns character varying
  immutable
  language plpgsql
as $$
declare
  v_split VARCHAR(40);
begin
  -- Empty value do nothing.
  if v_name is null or v_name = '' then
    return '';
  -- Could have 2 names separated by a comma. Or a suffix separated by a comma. Or last followed by a comma.
  -- Handle these first.
  elsif POSITION(',' in v_name) > 0 then
    v_split := TRIM(SPLIT_PART(v_name, ',', 1));
    -- If only 1 word before the comma, it is a last name in the format: last, first middle
    if split_part(v_split, ' ', 2) = '' then
      return split_part(v_split, ' ', 1);
    elsif split_part(v_split, ' ', 3) = '' then -- format is first last
      return split_part(v_split, ' ', 2);
    elsif split_part(v_split, ' ', 4) = '' then -- format is first middle last
      return split_part(v_split, ' ', 3);      
    else -- format first middle middle last
      return split_part(v_split, ' ', 4);      
    end if;
  elsif POSITION('/' in v_name) > 0 then -- 2 names separated by a slash
    v_split := TRIM(SPLIT_PART(v_name, '/', 1));
    if split_part(v_split, ' ', 2) = '' then -- last is after slash
      v_split := TRIM(SPLIT_PART(v_name, '/', 2));
    end if;
    if split_part(v_split, ' ', 4) != '' then -- format is first middle middle last
      return split_part(v_split, ' ', 4);
    elsif split_part(v_split, ' ', 3) != '' then -- format is first middle last
      return split_part(v_split, ' ', 3);
    elsif split_part(v_split, ' ', 2) != '' then -- format is first last
      return split_part(v_split, ' ', 2);
    else  -- format is last
      return split_part(v_split, ' ', 1);
    end if;
  else -- format first last or first middle last
    if split_part(v_name, ' ', 4) != '' then -- format is first middle middle last
      return split_part(v_name, ' ', 4);
    elsif split_part(v_name, ' ', 3) != '' then -- format is first middle last
      return split_part(v_name, ' ', 3);
    elsif split_part(v_name, ' ', 2) != '' then -- format is first last
      return split_part(v_name, ' ', 2);
    else  -- format is last
      return split_part(v_name, ' ', 1);
    end if;
  end if;
end;
$$;

--
-- legacy document.name extract submitting party individual first name
--
create or replace function public.mhr_conversion_individual_first(v_name character varying) returns character varying
  immutable
  language plpgsql
as $$
declare
  v_split VARCHAR(40);
begin
  -- Empty value do nothing.
  if v_name is null or v_name = '' then
    return '';
  -- Could have 2 names separated by a comma. Or a suffix separated by a comma. Or last followed by a comma.
  -- Handle these first.
  elsif POSITION(',' in v_name) > 0 then
    v_split := TRIM(SPLIT_PART(v_name, ',', 1));
    -- If only 1 word before the comma, the format is: last, first (middle)
    if split_part(v_split, ' ', 2) = '' then
      v_split := TRIM(SPLIT_PART(v_name, ',', 2));
      return split_part(v_split, ' ', 1);
    else -- first name is the first word
      return split_part(v_split, ' ', 1);
    end if;
  elsif POSITION('/' in v_name) > 0 then -- 2 names separated by a slash
    v_split := TRIM(SPLIT_PART(v_name, '/', 1));
    if split_part(v_split, ' ', 2) = '' then -- format is first1/first2 (middle) last
      return TRIM(SPLIT_PART(v_name, ' ', 1));
    else -- first name is always the first word.
      return split_part(v_split, ' ', 1); 
    end if;
  else -- format first (middle) last
    return split_part(v_name, ' ', 1);
  end if;
end;
$$;

--
-- legacy document.name extract submitting party individual middle name(s).
--
create or replace function public.mhr_conversion_individual_middle(v_name character varying) returns character varying
  immutable
  language plpgsql
as $$
declare
  v_split VARCHAR(40);
begin
  -- Empty value do nothing.
  if v_name is null or v_name = '' then
    return '';
  -- Could have 2 or 3 names separated by a comma. Or a suffix separated by a comma. Or last followed by a comma.
  -- Handle these first.
  elsif POSITION(',' in v_name) > 0 then
    v_split := TRIM(SPLIT_PART(v_name, ',', 1));
    -- If only 1 word before the comma, the format is: last, first (middle) and middle is after the comma.
    if split_part(v_split, ' ', 2) = '' then -- middle is not the first word
      v_split := TRIM(SPLIT_PART(v_name, ',', 2));
      if split_part(v_split, ' ', 4) != '' then
        return split_part(v_split, ' ', 2) || ' ' || split_part(v_split, ' ', 3) || ' ' || split_part(v_split, ' ', 4);
      elsif split_part(v_split, ' ', 3) != '' then
        return split_part(v_split, ' ', 2) || ' ' || split_part(v_split, ' ', 3);
      elsif split_part(v_split, ' ', 2) != '' then
        return split_part(v_split, ' ', 2);
      elsif SPLIT_PART(v_name, ',', 3) != '' then -- format is last, first, middle ...
        v_split := TRIM(SPLIT_PART(v_name, ',', 3));
        if split_part(v_split, ' ', 2) != '' then
          return split_part(v_split, ' ', 1);
        else
          return v_split;
        end if;
      end if;
    elsif split_part(v_split, ' ', 5) != '' then -- middle is not the first word and not the last word.
      return split_part(v_split, ' ', 2) || ' ' || split_part(v_split, ' ', 3) || ' ' || split_part(v_split, ' ', 4);
    elsif split_part(v_split, ' ', 4) != '' then
      return split_part(v_split, ' ', 2) || ' ' || split_part(v_split, ' ', 3);
    elsif split_part(v_split, ' ', 3) != '' then
      return split_part(v_split, ' ', 2);
    end if;
  elsif POSITION('/' in v_name) > 0 then -- 2 names separated by a slash
    v_split := TRIM(SPLIT_PART(v_name, '/', 1));
    if split_part(v_split, ' ', 2) = '' then -- format is first1/first2 (middle) last
      v_split := TRIM(SPLIT_PART(v_name, '/', 2));
    end if;
    
    if split_part(v_split, ' ', 5) != '' then
      return split_part(v_split, ' ', 2) || ' ' || split_part(v_split, ' ', 3) || ' ' || split_part(v_split, ' ', 4);
    elsif split_part(v_split, ' ', 4) != '' then
      return split_part(v_split, ' ', 2) || ' ' || split_part(v_split, ' ', 3);
    elsif split_part(v_split, ' ', 3) != '' then
      return split_part(v_split, ' ', 2);
    end if;
  else -- format first (middle) last
    if split_part(v_name, ' ', 5) != '' then -- middle is not the first word and not the last word.
      return split_part(v_name, ' ', 2) || ' ' || split_part(v_name, ' ', 3) || ' ' || split_part(v_name, ' ', 4);
    elsif split_part(v_name, ' ', 4) != '' then
      return split_part(v_name, ' ', 2) || ' ' || split_part(v_name, ' ', 3);
    elsif split_part(v_name, ' ', 3) != '' then
      return split_part(v_name, ' ', 2);
    end if;
  end if;
  return null;
end;
$$;

--
-- legacy document.name extract submitting party individual suffix.
--
create or replace function public.mhr_conversion_individual_suffix(v_name character varying) returns character varying
  immutable
  language plpgsql
as $$
declare
  v_split VARCHAR(40);
begin
  -- Empty value do nothing.
  if v_name is null or v_name = '' then
    return '';
  -- Could have 2 names separated by a comma. Or a suffix separated by a comma. Or last followed by a comma.
  -- Handle these first.
  elsif POSITION(',' in v_name) > 0 then
    v_split := TRIM(SPLIT_PART(v_name, ',', 1));
    -- If only 1 word before the comma, the format is: last, first (middle) with no suffix.
    if split_part(v_split, ' ', 2) != '' then -- suffix is everything after the comma.
      if SPLIT_PART(v_name, ',', 3) = '' then
        return TRIM(SPLIT_PART(v_name, ',', 2));
      else
        return TRIM(SPLIT_PART(v_name, ',', 2) || ',' || SPLIT_PART(v_name, ',', 3));
      end if;
    end if;
  elsif POSITION('/' in v_name) > 0 then -- 2 names separated by a slash
    v_split := TRIM(SPLIT_PART(v_name, '/', 1));
    if split_part(v_split, ' ', 2) != '' then  -- suffix is everything after the slash.
      return TRIM(SPLIT_PART(v_name, '/', 2));
    end if;
  end if;
  return null;
end;
$$;

--
-- Try and extract a region code from address text. 
--
create or replace function public.mhr_conversion_address_region(v_text character varying, v_replace boolean) returns character varying
  immutable
  language plpgsql
as $$
declare
  -- order is important within the array for removal
  bc_region text[] := '{", BC "," BC ",",BC ",",BC,","BC,","BC,"," B,.C. ",", B.C.",",B.C.",",B.C "," B.C."," B.C"," B . C. ",", B C. "' ||
                       ',"B.C. ","B C ","B..C","B. C. ","/BC/"," B,C, "," B\\C "," B,C. "," B.,C,. ",", CB ",", B. C> "' ||
                       ',", B. C "," B>C ",", B .C. "," BDC "," BXC "," B. .C "," CBC ","BRITISHCOLUMBIA","BRITISH COLUMBIA"' ||
                       ',"BRITSH COLUMBIA","BRITSH COLUMIA","BRITSH COLUMBIA","BTISH COLUMBIA","BRTISH COLUMBIA"' ||
                       ',"BRITSIH COLUMBIA","BRITIHS COLUMBIA","BRISITH COLUMBIA","BRISTISH COLUMBIA","BRISITSH COLUMBIA"' ||
                       ',"BRITISIH COLUMBIA","BRIRISH COLUMBIA","BRIISH COLUMBIA","BREITISH COLUMBIA","BRITISH COLUBIA"' ||
                       ',"BREITISH COLUMBIA","BRITISH COLUMVIA"," BC. ","BRITISH COLUMIBA"," B.B. "," BC- "," BCC ",",B .C. "' ||
                       '," BCD ", " BV "," BRITISH COLUMBI "," BRITISH  COLUMBIA "," BCV "," BCL "," BRITISH COUMBIA "," BE "' ||
                       '," BCS "," B C. "," BRITISH COLUBMIA "," BCY "," BCN "," B C, "," BX "," BRITISH COLIMBIA "," C.B. "' ||
                       '," BRITISH COLMBIA "," B.V. "," BRITISH COMUMBIA "," BGC "," BRITISH CLOUMBIA "," BCBC "," B .C "' ||
                       '," BRITISH COLUMBAI "," BRITISH COLUMIA "," BRITISH COLUMBIUA "," BRITISH COLULMBIA ", " V1BC "," VC "}';
  ab_region text[] := '{" AB "," A.B. "," AB, "," AB,"," AB. ",",AB ",",AB,"," ALTA "," ALTA. "," ALB ","ALBERT "," AL "' ||
                        ',"ALERTA ","ALBERTA ","ALBERTA,","ABLERTA ","ABERTA","ALBRTA","ALBETRA"," ALBERA "," ALBERTS " }';
  mb_region text[] := '{", MAN. "," MAN. "," MAN "," MB "," MB, "," MB,"," MB. ",",MB ",",MB","MANITOBA","MANAITOBA"' ||
                        ',"MANITOBE"}';
  sk_region text[] := '{" SK "," SK. ",", SK",", SA "," SA ","SASKATCHEWAN"," ASKATCHEWAN "," SASK. "," SASK "," SASKATACHEWAN "}';
  on_region text[] := '{" ONTARIO,"," ONTARIO "," ONTARION ","ONTARO"," ONTRIO "," ONT "," ONT. "," ON "," ON. ",", ON "' ||
                        ',",ON "," O.N. "," OT "}';
  qc_region text[] := '{" QC "," QC",", QC"," QUEBEC "," QUEBEC, "," QUE "," QU "," PQ "}';
  yt_region text[] := '{" YK "," YT ",", YT"," YUKON TERRITORIES "," YUKON TERRITORY "," YUKON "}';
  nb_region text[] := '{" NB ",", NB"," N.B. ","NEW BRUNSWICK"}';
  nl_region text[] := '{" NFLD "," NL "," N.L. ",", NL","NEWFOUNDLAND", " NF "}';
  ns_region text[] := '{" NS ",", NS","NOVA SCOTIA"}';
  nt_region text[] := '{" NWT "," N.W.T. "," N.T. "," NT ",", NT","NORTH WEST TERRITORIES","NORTHWEST TERRITORIES"}';
  nu_region text[] := '{" NUNUVIT "," NU ",", NU "}';
  pe_region text[] := '{" PEI "," P.E.I. "," PE ",", PE ","PRINCE EDWARD ISLAND"}';
  us_states text[] := ARRAY[ARRAY[' ALASKA ', 'AK'],
                            ARRAY[' ALASKA, ','AK'],
                            ARRAY[' AK ','AK'],
                            ARRAY[' AR ','AR'],
                            ARRAY[' ARKANSAS ','AR'],
                            ARRAY[' ARIZONA ','AZ'],
                            ARRAY[' ARIZONA,','AZ'],
                            ARRAY[' AZ ','AZ'],
                            ARRAY[' CALFORNIA ','CA'],
                            ARRAY[' CALIFORNIA ','CA'],
                            ARRAY[' CALIFORNIA,','CA'],
                            ARRAY[' CALIFORNAI ','CA'],                            
                            ARRAY[' CA ','CA'],
                            ARRAY[' CA. ','CA'],
                            ARRAY[' CA, ','CA'],
                            ARRAY['CALFORNIA','CA'],
                            ARRAY[' CALIF. ','CA'],
                            ARRAY[' CALIF ','CA'],
                            ARRAY[' CAL, ','CA'],
                            ARRAY[' COLORADO ','CO'],
                            ARRAY[' COLORADO, ','CO'],
                            ARRAY[' CO ','CO'],
                            ARRAY[' CO, ','CO'],
                            ARRAY['CONNECTICUT','CT'],
                            ARRAY[' CT ','CT'],
                            ARRAY[' FLORIDA ','FL'],
                            ARRAY[' FLORIDA, ','FL'],
                            ARRAY[' FL ','FL'],
                            ARRAY[' FL. ','FL'],
                            ARRAY[' GA ','GA'],
                            ARRAY[' GEORGIA ','GA'],
                            ARRAY[' HAWAII ','HI'],
                            ARRAY[' HAWAII, ','HI'],
                            ARRAY[' HI ','HI'],
                            ARRAY[' ID ','ID'],
                            ARRAY[' IDAHO ','ID'],
                            ARRAY['IDAHO ','ID'],
                            ARRAY['IDAHO,','ID'],
                            ARRAY['ILLINOIS','IL'],
                            ARRAY[' IL ','IL'],
                            ARRAY[' IA ','IA'],
                            ARRAY[' IOWA ','IA'],
                            ARRAY[' INDIANA ','IN'],
                            ARRAY[' IN ','IN'],
                            ARRAY[' KANSAS ','KS'],
                            ARRAY[' KS ','KS'],
                            ARRAY[' KY ','KY'],
                            ARRAY[' KEN. ','KY'],
                            ARRAY[' KENTUCKY ','KY'],
                            ARRAY[' LA ','LA'],
                            ARRAY[' LOUISIANA ','LA'],
                            ARRAY[' MONTANA ','MT'],
                            ARRAY[' MONTANA, ','MT'],
                            ARRAY[' MT ','MT'],
                            ARRAY['MASSACHUSETTS','MA'],
                            ARRAY[' MA ','MA'],
                            ARRAY[' MARYLAND ','MD'],
                            ARRAY[' MD ','MD'],
                            ARRAY['MICHIGAN','MI'],
                            ARRAY[' MI ','MI'],
                            ARRAY['MINNESOTA','MN'],
                            ARRAY[' MN ','MN'],
                            ARRAY[' MISSOURI ','MO'],
                            ARRAY[' MO ','MO'],
                            ARRAY[' NEBRASKA ','NE'],
                            ARRAY[' NE ','NE'],
                            ARRAY[' NEVADA ','NV'],
                            ARRAY[' NEVADA, ','NV'],
                            ARRAY[' NV ','NV'],
                            ARRAY[' NV. ','NV'],
                            ARRAY[' NORTH CAROLINA ','NC'],
                            ARRAY[' NC ','NC'],
                            ARRAY[' NORTH DAKOTA ','ND'],
                            ARRAY[' ND ','ND'],
                            ARRAY[' NEW YORK ','NY'],
                            ARRAY[' NY ','NY'],
                            ARRAY[' NY, ','NY'],
                            ARRAY[' OH ','OH'],
                            ARRAY[' OHIO,','OH'],
                            ARRAY[' OHIO ','OH'],
                            ARRAY[' OK ','OK'],
                            ARRAY[' OR. ','OR'],
                            ARRAY[' OR, ','OR'],
                            ARRAY[' OR ','OR'],
                            ARRAY[',OR ','OR'],
                            ARRAY[' OREGON ','OR'],
                            ARRAY[' ORGEON ','OR'],
                            ARRAY[', OREGON ','OR'],
                            ARRAY[' OREGON, ','OR'],
                            ARRAY[' OREGAN ','OR'],
                            ARRAY[', PA, ','PA'],
                            ARRAY[' PENNSYLVANIA ','PA'],
                            ARRAY[', PA, ','PA'],
                            ARRAY[' SOUTH CAROLINA ','SC'],
                            ARRAY[' SC ','SC'],
                            ARRAY[' TENNESSEE ','TN'],
                            ARRAY[' TENN. ','TN'],
                            ARRAY[' TN ','TN'],
                            ARRAY[' TEXAS ','TX'],
                            ARRAY[' TEXAS, ','TX'],
                            ARRAY[' TX ','TX'],
                            ARRAY[' TX. ','TX'],
                            ARRAY[' UT ','UT'],
                            ARRAY[' UTAH ','UT'],
                            ARRAY[' UTAH, ','UT'],
                            ARRAY[' VIRGINIA ','VA'],
                            ARRAY[' VIRGINIA, ','VA'],
                            ARRAY[' VA ','VA'],
                            ARRAY[' VERMONT ','VT'],
                            ARRAY[' VT ','VT'],
                            ARRAY[', WA ','WA'],
                            ARRAY[', WA. ','WA'],
                            ARRAY[' WA, ','WA'],
                            ARRAY[' WA ','WA'],
                            ARRAY[' WA ','WA'],
                            ARRAY[' WASHINGTON, DC ','DC'],
                            ARRAY[' DC ','DC'],
                            ARRAY[', WASHINGTON ','WA'],
                            ARRAY[' WAHINGTON ','WA'],
                            ARRAY[' WASHINGTON ','WA'],
                            ARRAY[' WASHINGTON,','WA'],
                            ARRAY[' WI ','WI'],
                            ARRAY[' WISCONSIN ','WI']];
  us_state text[];
begin
  -- Empty value do nothing.
  if v_text is null or v_text = '' then
    return '';
  -- Try Canada province codes first.
  else
     for i in 1 .. array_upper(bc_region, 1)
     loop
       if POSITION(bc_region[i] in v_text) > 0 then
         if v_replace then
           return bc_region[i];
         else
           return 'BC';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(ab_region, 1)
     loop
       if POSITION(ab_region[i] in v_text) > 0 then
         if v_replace then
           return ab_region[i];
         else
           return 'AB';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(sk_region, 1)
     loop
       if POSITION(sk_region[i] in v_text) > 0 then
         if v_replace then
           return sk_region[i];
         else
           return 'SK';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(mb_region, 1)
     loop
       if POSITION(mb_region[i] in v_text) > 0 then
         if v_replace then
           return mb_region[i];
         else
           return 'MB';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(on_region, 1)
     loop
       if POSITION(on_region[i] in v_text) > 0 then
         if v_replace then
           return on_region[i];
         else
           return 'ON';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(qc_region, 1)
     loop
       if POSITION(qc_region[i] in v_text) > 0 then
         if v_replace then
           return qc_region[i];
         else
           return 'QC';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(yt_region, 1)
     loop
       if POSITION(yt_region[i] in v_text) > 0 then
         if v_replace then
           return yt_region[i];
         else
           return 'YT';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(nb_region, 1)
     loop
       if POSITION(nb_region[i] in v_text) > 0 then
         if v_replace then
           return nb_region[i];
         else
           return 'NB';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(nl_region, 1)
     loop
       if POSITION(nl_region[i] in v_text) > 0 then
         if v_replace then
           return nl_region[i];
         else
           return 'NL';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(ns_region, 1)
     loop
       if POSITION(ns_region[i] in v_text) > 0 then
         if v_replace then
           return ns_region[i];
         else
           return 'NS';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(nt_region, 1)
     loop
       if POSITION(nt_region[i] in v_text) > 0 then
         if v_replace then
           return nt_region[i];
         else
           return 'NT';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(nu_region, 1)
     loop
       if POSITION(nu_region[i] in v_text) > 0 then
         if v_replace then
           return nu_region[i];
         else
           return 'NU';
         end if;
       end if;
     end loop;
     for i in 1 .. array_upper(pe_region, 1)
     loop
       if POSITION(pe_region[i] in v_text) > 0 then
         if v_replace then
           return pe_region[i];
         else
           return 'PE';
         end if;
       end if;
     end loop;
     -- Try US states if get to here.
     foreach us_state slice 1 in array us_states
     loop
       if POSITION(us_state[1] in v_text) > 0 then
         if v_replace then
           return us_state[1];
         else
           return us_state[2];
         end if;
       end if;
     end loop;
  end if;
  return null;
end;
$$;

--
-- Determine if a city is a BC city when no region, postal code, or country code. 
--
create or replace function public.mhr_conversion_is_bc_city(v_text character varying) returns boolean
  immutable
  language plpgsql
as $$
declare
  bc_cities text[] := '{"ABBOTSFORD","COOMBS","100 MILE HOUSE","BURNS LAKE","CASSIDY","CRANBROOK","FORT ST. JAMES","FORT ST. JOHN"' ||
                      ',"GABRIOLA ISLAND","HOUSTON","KELOWNA","NANAIMO","PORT ALBERNI","POWELL RIVER","QUATHIASKI COVE"' ||
                      ',"COWICHAN","PENTICTON","SUMMERLAND","PRINCE GEORGE","THETIS ISLAND","CHILLIWACK","LUMBY"' ||
                      ',"KAMLOOPS","FANNY BAY","GOLD RIVER","BOWEN ISLAND","CAMPBELL RIVER","VANCOUVER","FORT ST JAMES"' ||
                      ',"VANDERHOOF","AGASSIZ","LADYSMITH","CACHE CREEK","GARIBALDI HIGHLANDS","LOGAN LAKE","MATSQUI","LANGLEY"' ||
                      ',"LANTZVILLE","DAWSON CREEK","FORT NELSON","DUNCAN","PORT ALICE","COMOX","70 MILE HOUSE","MERRITT"' ||
                      ',"SPARWOOD","MISSION","CLEARWATER","HUDSON HOPE","SHAWNIGAN LAKE","KEREMEOS","ALDERGROVE","QUEEN CHARLOTTE"' ||
                      ',"WOSS LAKE","NANOOSE","ALDERGROVE","PORT HARDY","KIMBERLEY","SORRENTO","PORT CLEMENTS","LAZO","HIXON"' ||
                      ',"BARRIERE","DEROCHE","PEACHLAND","COQUITLAM","COBBLE HILL","BOSTON BAR","NEW DENVER","VALEMONT"' ||
                      ',"FORT ST JOHN","PARKSVILLE","MAYNE ISLAND","FT. ST. JOHN","VERNON","SAANICH","NELSON","MILL BAY"' ||
                      ',"PRITCHARD","TULAMEEN","PINANTAN LAKE","WESTHOLME","CHASE","TAPPEN","BELLA COOLA","PEMBERTON"' ||
                      ',"MERVILLE","COURTENAY","MONTNEY","LONE BUTTE","QUENSNEL","CANAL FLATS","MILLBAY","MOUNT LEHMAN"' ||
                      ',"ASHCROFT","CRESTON","GRAND FORKS","FRASER HWY","CASTLEGAR","SALMO","OLVIER","TERRACE","GENELLE"' ||
                      ',"ROCK CREEK","CHARLIEL LAKE","OSOYOOS","PACIFIC RIM HWY","BURNABY","AGASIZ","HOPE","150 MILE HOUSE"' ||
                      ',"CATCH CREEK","MAPLE RIDGE","WHITE ROCK","JAFFRAY","OKANAGAN FALLS","LAKE COUNTRY","MOUNT CURRIE"' ||
                      ',"FERNIE","SLOCAN","PRINCE RUPERT"' ||
                      ',"QUESNEL","REVELSTOKE","SALMON ARM","SURREY","VICTORIA","WESTBANK","WILLIAMS LAKE","QUALICUM","SOOKE"}';
begin
  -- Empty value do nothing.
  if v_text is null or v_text = '' then
    return false;
  -- Try Canada province codes first.
  else
     for i in 1 .. array_upper(bc_cities, 1)
     loop
       if POSITION(bc_cities[i] in v_text) > 0 then
         return true;
       end if;
     end loop;
  end if;
  return false;
end;
$$;

--
-- Try and extract a country code from address text and a region code. 
--
create or replace function public.mhr_conversion_address_country(v_text character varying, v_region character varying, v_replace boolean) returns character varying
  immutable
  language plpgsql
as $$
declare
  province_codes varchar(60) := ' BC AB SK MB ON QC PE YT NU NT NS NL NB ';
  state_codes varchar(200) := ' AK AR AZ CA CO CT FL GA HI ID IL IN KS KY LA MA MD MI MO MT MN ND NE NC NY NV OH OK OR PA SC' ||
                              'TN TX UT VA VT WA WI IA ME MO NH NJ NM ND PR RI SD VI WV WY ';
  countries text[] := ARRAY[ARRAY['U.S.A.', 'US'],
                            ARRAY['U.SA.','US'],
                            ARRAY[' USA ','US'],
                            ARRAY['USA ','US'],
                            ARRAY[' CA ','CA'],
                            ARRAY['CANADA','CA'],
                            ARRAY['BERMUDA','BM'],
                            ARRAY['BOTSWANA, AFRICA','BW'],
                            ARRAY['BOTSWANA','BW'],
                            ARRAY['ARMENIA','AM'],
                            ARRAY['AUSTRALIA','AU'],
                            ARRAY['AUSTRIA','AT'],
                            ARRAY['FRANCE UN','FR'],
                            ARRAY['FRANCE','FR'],
                            ARRAY['-GERMANY','DE'],
                            ARRAY['WEST GERMANY','DE'],
                            ARRAY['WEST GERMANU','DE'],
                            ARRAY['GERMANY','DE'],
                            ARRAY['HONG KONG ','HK'],
                            ARRAY['HONGKONG','HK'],
                            ARRAY[' HK ','HK'],
                            ARRAY['INDONESIA','ID'],
                            ARRAY['INDIA','IN'],
                            ARRAY['(ITALY) ITALIA','IT'],
                            ARRAY['JAPAN','JP'],
                            ARRAY['LATVIA','LV'],
                            ARRAY['MACAU','MO'],
                            ARRAY['MACAO','MO'],
                            ARRAY['MALTA','MT'],
                            ARRAY['MEXICO','MX'],
                            ARRAY['MALAYSIA','MY'],
                            ARRAY['MONGOLIA','MN'],
                            ARRAY['HOLLAND','NL'],
                            ARRAY['NETHERLANDS','NL'],
                            ARRAY['NETHERLAND','NL'],
                            ARRAY['NORWAY','NO'],
                            ARRAY['NEW ZEALAND','NZ'],
                            ARRAY['NORTHERN IRELAND','GB'],
                            ARRAY['PAPUA, NEW GUINEA','PG'],
                            ARRAY['PHILIPPINES','PH'],
                            ARRAY['PORTUGAL','PT'],
                            ARRAY['SCOTLAND','GB'],
                            ARRAY['SPAIN','ES'],
                            ARRAY[' SG ','SG'],
                            ARRAY['SWEDEN','SE'],
                            ARRAY['SWITZERLAND','CH'],
                            ARRAY['CHANNEL ISLANDS','GB'],
                            ARRAY['ENGLAND, UK','GB'],
                            ARRAY['ENGLABD','GB'],
                            ARRAY['ENGLAND','GB'],
                            ARRAY['U.A.E.','AE'],
                            ARRAY['UAE','AE'],
                            ARRAY['UNITED ARAB EMIRATES','AE'],
                            ARRAY['UNITED KINGDOM','GB'],
                            ARRAY['UNITED KINGDON','GB'],
                            ARRAY[' U.K. ','GB'],
                            ARRAY[' UK ','GB'],
                            ARRAY['VIETNAM','VN'],
                            ARRAY['ANGUILLA, BRITISH WEST INDIES','AI'],
                            ARRAY['TURKS AND CAICOS ISLANDSBRITISH WEST INDIES','TC']];
  country text[];
begin
  -- Empty value do nothing.
  if v_text is null or v_text = '' then
    return null;
  -- Try Canada province codes first.
  elsif v_region is not null and v_region != '' and POSITION(v_region in province_codes) > 0 then
    return 'CA';
  elsif v_region is not null and v_region != '' and POSITION(v_region in state_codes) > 0 then
    return 'US';
  else
     -- Try countries if get to here.
     foreach country slice 1 in array countries
     loop
       if POSITION(country[1] in v_text) > 0 then
         if v_replace then
           return country[1];
         else
           return country[2];
         end if;
       end if;
     end loop;
  end if;
  return null;
end;
$$;


--
-- Try and assign a country code of CA from address text that ends with a Canada postal code. 
--
create or replace function public.mhr_conversion_address_country_pcode(v_text character varying) returns character varying
  immutable
  language plpgsql
as $$
declare
  test_code varchar(15);
  replace_val varchar(40);
begin
  -- Empty value do nothing.
  if v_text is null or v_text = '' then
    return null;
  elsif LENGTH(TRIM(v_text)) >= 6 then
    test_code := REPLACE(RIGHT(TRIM(v_text), 7), ' ', '');
    test_code := REPLACE(test_code, '-', '');
    if REGEXP_MATCHES(test_code,'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$','gi') is not null then
      return 'CA';
    end if;
  end if;
  return null;
end;
$$;

--
-- Remove region and country text from address text after region and country have been extracted from the address text. 
--
create or replace function public.mhr_conversion_address_remove(v_text character varying) returns character varying
  immutable
  language plpgsql
as $$
declare
  new_text varchar(125);
  replace_val varchar(40);
begin
  -- Empty value do nothing.
  if v_text is null or v_text = '' then
    return '';
  else
    -- try removing region text
    new_text := ' ' || v_text || ' ';
    replace_val := mhr_conversion_address_region(new_text, true);
    if replace_val != '' and position('QUEBEC' in replace_val) < 1 then
      new_text := TRIM(REPLACE(new_text, replace_val, ' '));
    end if;
    -- try removing country text
    new_text := ' ' || new_text || ' ';
    replace_val := mhr_conversion_address_country(v_text, '', true);
    if replace_val != '' then
      new_text := TRIM(REPLACE(new_text, replace_val, ''));
    end if;
    if LENGTH(new_text) > 0 and RIGHT(new_text, 1) = ',' then
      new_text := TRIM(SUBSTR(new_text, 1, (LENGTH(new_text) - 1)));
    end if;
    return TRIM(new_text);
  end if;
end;
$$;

--
-- Try and extract a Canada or US postal code from address text. 
--
create or replace function public.mhr_conversion_address_pcode(v_text character varying, v_country character varying, v_replace boolean) returns character varying
  immutable
  language plpgsql
as $$
declare
  test_code varchar(15);
  match varchar(15);
begin
  -- Empty value do nothing.
  if v_text is null or LENGTH(v_text) < 7 or v_country = '' then
    return null;
  elsif v_country = 'CA' then
    test_code := REPLACE(RIGHT(v_text, 7), ' ', '');
    test_code := REPLACE(test_code, '-', '');
    if REGEXP_MATCHES(test_code,'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$','gi') is not null then
      if v_replace then
        return RIGHT(v_text, 7);
      else
        return SUBSTR(test_code, 1, 3) || ' ' || SUBSTR(test_code, 4);
      end if;
    end if;
  elsif v_country = 'US' and LENGTH(v_text) > 10 then
    test_code := REPLACE(RIGHT(v_text, 11), ' ', '');
    if REGEXP_MATCHES(test_code,'^\d{5}(-{0,1}\d{4})?$','gi') is not null then
      if v_replace then
        return RIGHT(v_text, 11);
      else
        return test_code;
      end if;
    else
      test_code := RIGHT(v_text, 5);
      if REGEXP_MATCHES(test_code,'^\d{5}$','gi') is not null then
        return test_code;
      end if;
    end if;
  end if;
  return null;
end;
$$;


--
-- By address text and optional postal code text parce into modernized address properties with a unique address id. 
--
create or replace function public.mhr_conversion_address(v_text character varying,
                                                         v_pcode character varying,
                                                         out address_id integer,
                                                         out street varchar(40),
                                                         out street_add varchar(50),
                                                         out city varchar(40),
                                                         out region varchar(2),
                                                         out pcode varchar(15),
                                                         out country varchar(2)) --returns integer
  immutable
  language plpgsql
as $$
declare
  test_pcode varchar(15);
  temp varchar(125);
  line_2 varchar(50);
  line_3 varchar(50);
  line_4 varchar(50);
begin
  -- Empty value do nothing.
  if v_text is null or v_text = '' then
    address_id := 0;
    return;
  else
    street := TRIM(SUBSTR(v_text, 1, 40));
    temp := ' ' || SUBSTR(v_text, 41) || ' ';
    region := mhr_conversion_address_region(temp, false);
    country := mhr_conversion_address_country(temp, region, false);
    -- Try to get country, region if postal code exists and no country or region.
    if country is null or country = '' then
      if v_pcode is not null and v_pcode != '' then 
        country := mhr_conversion_address_country_pcode(v_pcode);
      else
        country := mhr_conversion_address_country_pcode(temp);
      end if;
      if country is not null and region is null then
        region := 'BC';
      end if;
    end if;
    line_2 := mhr_conversion_address_remove(SUBSTR(v_text, 41, 40));
    if LENGTH(TRIM(v_text)) > 80 then
      line_3 := mhr_conversion_address_remove(SUBSTR(v_text, 81, 40));
    end if;    
    if LENGTH(TRIM(v_text)) > 120 then
      line_4 := mhr_conversion_address_remove(SUBSTR(v_text, 121));
    end if;
    -- Try to extract postal code here: it's always at the end if present.
    -- For owners, postal code is in a separate column but could also be in the address text. Need to check and remove.
    if LENGTH(line_4) > 0 then
      test_pcode := mhr_conversion_address_pcode(line_4, country, true);
    elsif LENGTH(line_3) > 0 then
      test_pcode := mhr_conversion_address_pcode(line_3, country, true);
    elsif LENGTH(line_2) > 0 then
      test_pcode := mhr_conversion_address_pcode(line_2, country, true);
    end if;
    if LENGTH(test_pcode) > 0 and (v_pcode is null or v_pcode = '') then
      pcode := test_pcode;
    elsif v_pcode is not null and v_pcode != '' then
      pcode := v_pcode;
    end if;
    if LENGTH(pcode) > 0 then
      if LENGTH(line_4) > 0 then
        line_4 := REPlACE(line_4, pcode, '');
      elsif LENGTH(line_3) > 0 then
        line_3 := REPlACE(line_3, pcode, '');
      elsif LENGTH(line_2) > 0 then
        line_2 := REPlACE(line_2, pcode, '');
      end if;
    end if;
    
    -- City is line 4 if lines 2 and 3 are empty.
    -- City is line 3 if line 2 is empty and lines 3 and 4 are not empty
    -- City is line 2 if lines 3 and 4 are empty.
    -- Here region and country, postal code have been removed.
    if line_4 != '' then
      city := line_4;
      if LENGTH(line_2) > 0 then
        street_add := line_2;
        if LENGTH(line_3) > 0 then
          street_add := SUBSTR((street_add || ' ' || line_3), 1, 50);
        end if;
      elsif LENGTH(line_3) > 0 then
        street_add := line_3;
      end if;
    elsif LENGTH(line_3) > 0 then
      city := line_3;
      if LENGTH(line_2) > 0 then
        street_add := line_2;
      end if;
    elsif LENGTH(line_2) > 0 then
      city := line_2;
    else -- After removing region, country, pcode only line 1 is non-empty.
      if region is null and country is null then
        temp := ' ' || SUBSTR(v_text, 1, 40) || ' ';
        region := mhr_conversion_address_region(temp, false);
        country := mhr_conversion_address_country(temp, region, false);
        if country is null or country = '' and pcode is not null then
          country := mhr_conversion_address_country_pcode(pcode);
        end if;
        if country is not null and region is null then
          region := 'BC';
        end if;
      end if;      
      street := mhr_conversion_address_remove(SUBSTR(v_text, 1, 40));
      if pcode is null then
        test_pcode := mhr_conversion_address_pcode(street, country, true);
        if LENGTH(test_pcode) > 0 then
          pcode := test_pcode;
          street := TRIM(REPlACE(street, pcode, ''));
        end if;
      end if;
    end if;

    if LENGTH(pcode) > 0 and country = 'CA' then
      pcode := TRIM(pcode);
      if LENGTH(pcode) = 6 then
        pcode := SUBSTR(pcode, 1, 3) || ' ' || SUBSTR(pcode, 4);
      else
        pcode := SUBSTR(pcode, 1, 3) || ' ' || SUBSTR(pcode, 5);        
      end if;
    end if;

    if LENGTH(city) > 0 and RIGHT(city, 1) = ',' then
      city := TRIM(SUBSTR(city, 1, (LENGTH(city) - 1)));
    end if;
    address_id := nextval('staging_mhr_address_id_seq');
  end if;  
end;
$$;

--
-- By document ID pattern create staging address table records from staging_mhr_document data and update 
-- the staging_mhr_document.address_id.
--
create or replace function public.mhr_conversion_address_document(v_doc_pattern character varying, v_is_business boolean) returns integer
  language plpgsql
as $$
declare
  cur_bus cursor(p_doc_pattern character varying) 
             for select address 
                   from staging_mhr_document 
                  where documtid like p_doc_pattern || '%'
                    and address is not null
                    and business_name is not null;
  cur_bus_default cursor 
             for select address 
                   from staging_mhr_document 
                  where address is not null
                    and business_name is not null
                    and address_id is null;
  cur_ind cursor(p_doc_pattern character varying) 
             for select address 
                   from staging_mhr_document 
                  where documtid like p_doc_pattern || '%'
                    and address is not null
                    and last_name is not null;
  cur_ind_default cursor 
             for select address 
                   from staging_mhr_document 
                  where address is not null
                    and last_name is not null
                    and address_id is null;
  rec_address record;
  counter integer := 0;
  addr_id integer := 0;
  street varchar(50);
  street_add varchar(50);
  city varchar(40);
  pcode varchar(15);
  region varchar(2);
  country varchar(2);
begin
  if v_is_business then
    if v_doc_pattern != '' then
      open cur_bus(v_doc_pattern);
      loop
        fetch cur_bus into rec_address;
        exit when not found;
        counter := counter + 1;
        select * 
          from mhr_conversion_address(rec_address.address, '')
          into addr_id, street, street_add, city, region, pcode, country;
        insert into staging_mhr_addresses values(addr_id, street, street_add, city, region, pcode, country);
        update staging_mhr_document set address_id = addr_id where current of cur_bus;
      end loop;
      close cur_bus;
    else
      open cur_bus_default;
      loop
        fetch cur_bus_default into rec_address;
        exit when not found;
        counter := counter + 1;
        select * 
          from mhr_conversion_address(rec_address.address, '')
          into addr_id, street, street_add, city, region, pcode, country;
        insert into staging_mhr_addresses values(addr_id, street, street_add, city, region, pcode, country);
        update staging_mhr_document set address_id = addr_id where current of cur_bus_default;
      end loop;
      close cur_bus_default;
    end if;
  else
    if v_doc_pattern != '' then
      open cur_ind(v_doc_pattern);
      loop
        fetch cur_ind into rec_address;
        exit when not found;
        counter := counter + 1;
        select * 
          from mhr_conversion_address(rec_address.address, '')
          into addr_id, street, street_add, city, region, pcode, country;
        insert into staging_mhr_addresses values(addr_id, street, street_add, city, region, pcode, country);
        update staging_mhr_document set address_id = addr_id where current of cur_ind;
      end loop;
      close cur_ind;
    else
      open cur_ind_default;
      loop
        fetch cur_ind_default into rec_address;
        exit when not found;
        counter := counter + 1;
        select * 
          from mhr_conversion_address(rec_address.address, '')
          into addr_id, street, street_add, city, region, pcode, country;
        insert into staging_mhr_addresses values(addr_id, street, street_add, city, region, pcode, country);
        update staging_mhr_document set address_id = addr_id where current of cur_ind_default;
      end loop;
      close cur_ind_default;
    end if;
  end if;
  return counter;
end;
$$;

--
-- By manhomid range create staging address table records from staging_mhr_owner data and update 
-- the staging_mhr_owner.address_id.
--
create or replace function public.mhr_conversion_address_owner(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_owners cursor(p_start integer, p_end integer) 
             for select ownraddr, ownrpoco 
                   from staging_mhr_owner 
                  where manhomid between p_start and p_end;
  rec_owner record;
  counter integer := 0;
  addr_id integer := 0;
  street varchar(50);
  street_add varchar(50);
  city varchar(40);
  pcode varchar(15);
  region varchar(2);
  country varchar(2);
begin
  open cur_owners(v_start_id, v_end_id);
  loop
    fetch cur_owners into rec_owner;
    exit when not found;
    counter := counter + 1;
    if rec_owner.ownraddr is not null then
      select * 
        from mhr_conversion_address(rec_owner.ownraddr, rec_owner.ownrpoco)
        into addr_id, street, street_add, city, region, pcode, country;
      insert into staging_mhr_addresses values(addr_id, street, street_add, city, region, pcode, country);
    else
      addr_id := nextval('staging_mhr_address_id_seq');
      insert into staging_mhr_addresses values(addr_id, null, null, null, null, null, null);
    end if;
    update staging_mhr_owner set address_id = addr_id where current of cur_owners;
  end loop;
  close cur_owners;
  return counter;
end;
$$;

--
-- Create staging address table records from staging_mhr_note data and update the staging_mhr_note.address_id.
-- Conditional on the note contact being different from the document submitting party.
--
create or replace function public.mhr_conversion_address_note() returns integer
  language plpgsql
as $$
declare
  cur_notes cursor 
            for select n.address 
                  from staging_mhr_note n
                 where n.name IS NOT NULL
                   and n.address IS NOT NULL
                   and n.regdocid in (select d.documtid
                                        from staging_mhr_document d
                                       where d.documtid = n.regdocid
                                         and d.address IS NOT NULL
                                         and d.address != n.address);
  rec_note record;
  counter integer := 0;
  addr_id integer := 0;
  street varchar(50);
  street_add varchar(50);
  city varchar(40);
  pcode varchar(15);
  region varchar(2);
  country varchar(2);
begin
  open cur_notes;
  loop
    fetch cur_notes into rec_note;
    exit when not found;
    counter := counter + 1;
    select * 
      from mhr_conversion_address(rec_note.address, '')
      into addr_id, street, street_add, city, region, pcode, country;
    insert into staging_mhr_addresses values(addr_id, street, street_add, city, region, pcode, country);
    update staging_mhr_note set address_id = addr_id where current of cur_notes;
  end loop;
  close cur_notes;
  return counter;
end;
$$;

--
-- By manhomid range create staging address table records from staging_mhr_location data and update 
-- the staging_mhr_location.address_id.
--
create or replace function public.mhr_conversion_address_location(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_addresses cursor(p_start integer, p_end integer)
            for select stnumber, stname, towncity, province 
                  from staging_mhr_location
                 where manhomid between p_start and p_end;
--                 where towncity is not null
--                   and manhomid between p_start and p_end;
  province_codes varchar(60) := ' BC AB SK MB ON QC PE YT NU NT NS NL NB ';
  state_codes varchar(200) := ' AK AR AZ CA CO CT FL GA HI ID IL IN KS KY LA MA MD MI MO MT MN ND NE NC NY NV OH OK OR PA SC' ||
                              'TN TX UT VA VT WA WI ';
  rec_address record;
  counter integer := 0;
  addr_id integer := 0;
  street varchar(50);
  city varchar(40);
  region varchar(2);
  country varchar(2) := 'CA';
begin
  open cur_addresses(v_start_id, v_end_id);
  loop
    fetch cur_addresses into rec_address;
    exit when not found;
    counter := counter + 1;

    if rec_address.province is not null then   
        if POSITION(rec_address.province in province_codes) > 0 then
          region := rec_address.province;
          country := 'CA';
        elsif POSITION(rec_address.province in state_codes) > 0 then
          region := rec_address.province;
          country := 'US';
        elsif rec_address.province = 'AL' then
          region := 'AB';
          country := 'CA';
        elsif rec_address.province = 'YK' then
          region := 'YT';
          country := 'CA';
        elsif rec_address.province = 'SA' then
          region := 'SK';
          country := 'CA';
        elsif rec_address.province = 'MA' then
          region := 'MB';
          country := 'CA';
        elsif rec_address.province = 'NF' then
          region := 'NL';
          country := 'CA';
        elsif rec_address.province = 'PQ' then
          region := 'QC';
          country := 'CA';
        elsif rec_address.province in ('WS', 'XX') then
          region := 'WA';
          country := 'US';
        elsif rec_address.province = 'US' then
          country := 'US';
          if rec_address.towncity is not null and LEFT(rec_address.towncity, 5) != 'BIRCH' then
            region := 'ID';
          else
            region := 'WA';
          end if;
        end if;
    end if;
    if rec_address.stnumber is not null and rec_address.stnumber != '' then
      street := rec_address.stnumber || ' ' || rec_address.stname;
    else
      street := rec_address.stname;
    end if;
    city := rec_address.towncity;    
    addr_id := nextval('staging_mhr_address_id_seq');
    insert into staging_mhr_addresses values(addr_id, street, null, city, region, null, country);
    update staging_mhr_location set address_id = addr_id where current of cur_addresses;
  end loop;
  close cur_addresses;
  return counter;
end;
$$;

--
-- Insert into mhr_locations by registration id range from staging_mhr_location.
--
create or replace function public.mhr_conversion_location(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_locations cursor(p_start integer, p_end integer) 
             for select * 
                   from staging_mhr_location
                  where registration_id between p_start and p_end;
  rec_loc record;
  counter integer := 0;
begin
  open cur_locations(v_start_id, v_end_id);
  loop
    fetch cur_locations into rec_loc;
    exit when not found;
    
    counter := counter + 1;
    insert into mhr_locations (id, registration_id, change_registration_id, location_type, status_type, address_id,
                               additional_description, dealer_name, exception_plan, leave_province, tax_certification,
                               tax_certification_date, park_name, park_pad, pid_number, lot, parcel, block, district_lot,
                               part_of, section, township, range, meridian, land_district, plan)
           values(nextval('mhr_location_id_seq'), rec_loc.registration_id, rec_loc.registration_id, rec_loc.location_type::mhr_location_type,
                  rec_loc.status_type::mhr_status_type, rec_loc.address_id, rec_loc.adddesc, rec_loc.mhdealer, rec_loc.excplan,
                  rec_loc.leavebc, rec_loc.taxcert, rec_loc.tax_certification_date, rec_loc.mahpname, rec_loc.mahppad, 
                  rec_loc.pidnumb, rec_loc.lot, rec_loc.parcel, rec_loc.block, rec_loc.distlot, rec_loc.partof, rec_loc.section,
                  rec_loc.township, rec_loc.range, rec_loc.meridian, rec_loc.landdist, rec_loc.plan);
  end loop;
  close cur_locations;
  return counter;
end;
$$;

--
-- Insert into mhr_descriptions and mhr_sections by registration id range from staging_mhr_description.
--
create or replace function public.mhr_conversion_description(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_descriptions cursor(p_start integer, p_end integer) 
             for select * 
                   from staging_mhr_description
                  where registration_id between p_start and p_end;
  rec_desc record;
  counter integer := 0;
begin
  open cur_descriptions(v_start_id, v_end_id);
  loop
    fetch cur_descriptions into rec_desc;
    exit when not found;
    
    counter := counter + 1;
    insert into mhr_descriptions (id, registration_id, change_registration_id, status_type, csa_number, csa_standard, 
                                  number_of_sections, square_feet, year_made, circa, engineer_date, engineer_name, 
                                  manufacturer_name, make, model, rebuilt_remarks, other_remarks)
           values(nextval('mhr_description_id_seq'), rec_desc.registration_id, rec_desc.registration_id,
                  rec_desc.status_type::mhr_status_type, rec_desc.csanumbr, rec_desc.csastand, rec_desc.numbsect, 
                  rec_desc.sqarfeet, CAST (rec_desc.yearmade AS INTEGER), rec_desc.circa, rec_desc.engineer_date, rec_desc.enginame, 
                  rec_desc.manuname, rec_desc.makemodl, null, rec_desc.rebuiltr, rec_desc.otherrem);

    if rec_desc.sernumb1 is not null then
      insert into mhr_sections (id, registration_id, change_registration_id, status_type, compressed_key, serial_number,
                                length_feet, length_inches, width_feet, width_inches)
             values(nextval('mhr_section_id_seq'), rec_desc.registration_id, rec_desc.registration_id,
                    rec_desc.status_type::mhr_status_type, mhr_serial_compressed_key(rec_desc.sernumb1), rec_desc.sernumb1,
                    rec_desc.length1, rec_desc.lengin1, rec_desc.width1, rec_desc.widin1);
    end if;
    if rec_desc.sernumb2 is not null then
      insert into mhr_sections (id, registration_id, change_registration_id, status_type, compressed_key, serial_number,
                                length_feet, length_inches, width_feet, width_inches)
             values(nextval('mhr_section_id_seq'), rec_desc.registration_id, rec_desc.registration_id,
                    rec_desc.status_type::mhr_status_type, mhr_serial_compressed_key(rec_desc.sernumb2), rec_desc.sernumb2,
                    rec_desc.length2, rec_desc.lengin2, rec_desc.width2, rec_desc.widin2);
    end if;
    if rec_desc.sernumb3 is not null then
      insert into mhr_sections (id, registration_id, change_registration_id, status_type, compressed_key, serial_number,
                                length_feet, length_inches, width_feet, width_inches)
             values(nextval('mhr_section_id_seq'), rec_desc.registration_id, rec_desc.registration_id,
                    rec_desc.status_type::mhr_status_type, mhr_serial_compressed_key(rec_desc.sernumb3), rec_desc.sernumb3,
                    rec_desc.length3, rec_desc.lengin3, rec_desc.width3, rec_desc.widin3);
    end if;
    if rec_desc.sernumb4 is not null then
      insert into mhr_sections (id, registration_id, change_registration_id, status_type, compressed_key, serial_number,
                                length_feet, length_inches, width_feet, width_inches)
             values(nextval('mhr_section_id_seq'), rec_desc.registration_id, rec_desc.registration_id,
                    rec_desc.status_type::mhr_status_type, mhr_serial_compressed_key(rec_desc.sernumb4), rec_desc.sernumb4,
                    rec_desc.length4, rec_desc.lengin4, rec_desc.width4, rec_desc.widin4);
    end if;

  end loop;
  close cur_descriptions;
  return counter;
end;
$$;

--
-- Insert into mhr_owner_groups by registration id range from staging_mhr_owngroup.
--
create or replace function public.mhr_conversion_owngroup(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_groups cursor(p_start integer, p_end integer) 
             for select * 
                   from staging_mhr_owngroup
                  where registration_id between p_start and p_end;
  rec_group record;
  counter integer := 0;
begin
  open cur_groups(v_start_id, v_end_id);
  loop
    fetch cur_groups into rec_group;
    exit when not found;
    
    counter := counter + 1;
    insert into mhr_owner_groups (id, registration_id, change_registration_id, sequence_number, tenancy_type, status_type, interest,
                                  interest_numerator, tenancy_specified, interest_denominator)
           values(nextval('mhr_owner_group_id_seq'), rec_group.registration_id, rec_group.registration_id, rec_group.owngrpid, 
                  rec_group.tenancy_type::mhr_tenancy_type, rec_group.status_type::mhr_owner_status_type, rec_group.interest,
                  rec_group.interest_numerator, rec_group.tenyspec, rec_group.interest_denominator);

  end loop;
  close cur_groups;
  return counter;
end;
$$;

--
-- Insert into mhr_parties by registration id range from staging_mhr_owner.
--
create or replace function public.mhr_conversion_owner(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_owners cursor(p_start integer, p_end integer) 
             for select o.*, sog.status_type, 
                 (select og.id 
                    from mhr_owner_groups og
                   where og.registration_id = o.registration_id
                     and og.sequence_number = o.owngrpid
                     fetch first 1 rows only) as owner_group_id 
                   from staging_mhr_owner o, staging_mhr_owngroup sog
                  where o.registration_id between p_start and p_end
                    and sog.registration_id = o.registration_id
                    and sog.owngrpid = o.owngrpid;
  rec_owner record;
  counter integer := 0;
begin
  open cur_owners(v_start_id, v_end_id);
  loop
    fetch cur_owners into rec_owner;
    exit when not found;
    
    counter := counter + 1;    
    if rec_owner.business_name is not null then
      insert into mhr_parties (id, registration_id, change_registration_id, party_type, status_type, address_id, compressed_name,
                               business_name, phone_number, owner_group_id, description, suffix)
             values(nextval('mhr_party_id_seq'), rec_owner.registration_id, rec_owner.registration_id, rec_owner.party_type::mhr_party_type,
                            rec_owner.status_type::mhr_owner_status_type, rec_owner.address_id,
                            mhr_name_compressed_key(rec_owner.ownrname), rec_owner.business_name, rec_owner.ownrfone,
                            rec_owner.owner_group_id, rec_owner.description, rec_owner.ownrsuff);
    elsif rec_owner.last_name is not null then
      insert into mhr_parties (id, registration_id, change_registration_id, party_type, status_type, address_id, compressed_name,
                               last_name, first_name, middle_name, phone_number, owner_group_id, description, suffix)
             values(nextval('mhr_party_id_seq'), rec_owner.registration_id, rec_owner.registration_id, rec_owner.party_type::mhr_party_type,
                            rec_owner.status_type::mhr_owner_status_type, rec_owner.address_id, mhr_name_compressed_key(rec_owner.ownrname),
                            rec_owner.last_name, rec_owner.first_name, rec_owner.middle_name, rec_owner.ownrfone,
                            rec_owner.owner_group_id, rec_owner.description, rec_owner.ownrsuff);
    end if;    

  end loop;
  close cur_owners;
  return counter;
end;
$$;

--
-- Insert into mhr_notes by registration id range from staging_mhr_note.
-- Insert into mhr_parties if contact name and address exist.
--
create or replace function public.mhr_conversion_note(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_notes cursor(p_start integer, p_end integer) 
             for select n.*, 
                 (select d.id 
                    from mhr_documents d
                   where d.registration_id = n.registration_id) as document_id 
                   from staging_mhr_note n
                  where n.registration_id between p_start and p_end;
  rec_note record;
  counter integer := 0;
begin
  open cur_notes(v_start_id, v_end_id);
  loop
    fetch cur_notes into rec_note;
    exit when not found;
    
    counter := counter + 1;
    insert into mhr_notes (id, registration_id, change_registration_id, status_type, document_type, document_id, remarks,
                           destroyed, expiry_date)
           values(nextval('mhr_note_id_seq'), rec_note.registration_id, rec_note.registration_id, 
                  rec_note.status_type::mhr_note_status_type, rec_note.docutype::mhr_document_type, rec_note.document_id,
                  rec_note.remarks, rec_note.destroyd, rec_note.expiry_date);

    if rec_note.address_id is not null and rec_note.business_name is not null then
      insert into mhr_parties (id, registration_id, change_registration_id, party_type, status_type, address_id, compressed_name,
                               business_name, phone_number)
             values(nextval('mhr_party_id_seq'), rec_note.registration_id, rec_note.registration_id, 'CONTACT',
                            'ACTIVE', rec_note.address_id,
                            mhr_name_compressed_key(rec_note.name), rec_note.business_name, rec_note.phone);
    elsif rec_note.address_id is not null and rec_note.last_name is not null then
      insert into mhr_parties (id, registration_id, change_registration_id, party_type, status_type, address_id, compressed_name,
                               last_name, first_name, middle_name, phone_number)
             values(nextval('mhr_party_id_seq'), rec_note.registration_id, rec_note.registration_id, 'CONTACT',
                            'ACTIVE', rec_note.address_id, mhr_name_compressed_key(rec_note.name),
                            rec_note.last_name, rec_note.first_name, rec_note.middle_name, rec_note.phone);
    end if;    

  end loop;
  close cur_notes;
  return counter;
end;
$$;

--
-- Insert in mhr_registrations, mhr_documents by registration id range from staging_mhr_document as a source.
--
create or replace function public.mhr_conversion_registration(v_start_id integer, v_end_id integer) returns integer
  language plpgsql
as $$
declare
  cur_documents cursor(p_start integer, p_end integer) 
             for select * 
                   from staging_mhr_document 
                  where registration_id between p_start and p_end;
  rec_doc record;
  counter integer := 0;
begin
  open cur_documents(v_start_id, v_end_id);
  loop
    fetch cur_documents into rec_doc;
    exit when not found;
    
    counter := counter + 1;
    insert into mhr_registrations (id, mhr_number, account_id, registration_type, registration_ts, status_type, draft_id,
                                   pay_invoice_id, pay_path, user_id, client_reference_id, document_id)
           values(rec_doc.registration_id, rec_doc.mhregnum, '0', rec_doc.registration_type::mhr_registration_type, rec_doc.registration_ts,
                  rec_doc.status_type::mhr_registration_status_type, 0, null, null, null, rec_doc.olbcfoli, rec_doc.documtid);
                  
    insert into mhr_documents (id, registration_id, document_type, document_id, document_registration_number, attention_reference,
                               declared_value, consideration_value, own_land, transfer_date, consent, owner_x_reference,
                               change_registration_id, affirm_by)
           values(nextval('mhr_document_id_seq'), rec_doc.registration_id, rec_doc.docutype::mhr_document_type, rec_doc.documtid,
                  rec_doc.docuregi, rec_doc.attnref, rec_doc.decvalue, rec_doc.convalue, rec_doc.ownland, rec_doc.transfer_date,
                  rec_doc.consent, rec_doc.ownrxref, rec_doc.registration_id, rec_doc.affirmby);

    if rec_doc.address_id is not null and rec_doc.business_name is not null then
      insert into mhr_parties (id, registration_id, change_registration_id, party_type, status_type, address_id, compressed_name,
                               business_name, phone_number)
             values(nextval('mhr_party_id_seq'), rec_doc.registration_id, rec_doc.registration_id, 'SUBMITTING', 'ACTIVE',
                            rec_doc.address_id, mhr_name_compressed_key(rec_doc.name), rec_doc.business_name, rec_doc.phone);
    elsif rec_doc.address_id is not null and rec_doc.last_name is not null then
      insert into mhr_parties (id, registration_id, change_registration_id, party_type, status_type, address_id, compressed_name,
                               last_name, first_name, middle_name, phone_number)
             values(nextval('mhr_party_id_seq'), rec_doc.registration_id, rec_doc.registration_id, 'SUBMITTING', 'ACTIVE',
                            rec_doc.address_id, mhr_name_compressed_key(rec_doc.name), rec_doc.last_name, rec_doc.first_name, 
                            rec_doc.middle_name, rec_doc.phone);
    end if;    
  end loop;
  close cur_documents;

  perform mhr_conversion_location(v_start_id, v_end_id);
  perform mhr_conversion_description(v_start_id, v_end_id);
  perform mhr_conversion_owngroup(v_start_id, v_end_id);
  perform mhr_conversion_owner(v_start_id, v_end_id);
  perform mhr_conversion_note(v_start_id, v_end_id);
  
  return counter;
end;
$$;

--
-- Insert registriations by registration id in batches of v_increment size.
--
create or replace function public.mhr_conversion_registration_all(v_increment integer) returns integer
  language plpgsql
as $$
declare
  v_counter integer := 0;
  v_total integer := 0;
  v_start_id integer := 1;
  v_end_id integer := 1;
  v_last_id integer := 2;
begin
  -- v_last_id := select max(registration_id) from staging_mhr_document;
  v_end_id := v_increment;
  raise INFO '% mhr_conversion_registration_all starting: increment=%, last id=%', now(), v_increment, v_last_id;
  while v_start_id <= v_last_id loop
    v_counter := mhr_conversion_registration(v_start_id, v_end_id);
    v_total := v_total + v_counter;
    v_start_id := v_start_id + v_increment;
    v_end_id := v_end_id + v_increment;
    raise INFO '% created % registrations. Updated start id=%, end id=%', now(), v_counter, v_start_id, v_end_id;
  end loop;  
  
  return v_total;
end;
$$;

--
-- Generated registration id's in the sequence of the document registration timestamps.
-- Replaces update below that does not always work
--
create or replace function public.mhr_conversion_reg_id() returns integer
  language plpgsql
as $$
declare
  cur_doc cursor 
            for select documtid, registration_ts
                  from staging_mhr_document
              order by registration_ts;
  rec_doc record;
  reg_id integer;
  counter integer := 0;
begin
  open cur_doc;
  loop
    fetch cur_doc into rec_doc;
    exit when not found;
    counter := counter + 1;
    reg_id := nextval('staging_mhr_reg_id_seq');
    update staging_mhr_document set registration_id = reg_id where documtid = rec_doc.documtid;
  end loop;
  close cur_doc;
  return counter;
end;
$$;

