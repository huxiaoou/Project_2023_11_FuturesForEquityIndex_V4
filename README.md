# Model Summary

## Differences or Improvements

+ derived from E:\Deploy\Projects\CTA3\
+ change universe from COMMODITY to EQUITY
+ remove factor RS(or Registered Stock), which is not applied to EQUITY futures
+ rewrite factor BASIS, for a direction basis data is not available
+ reset project data from  E:\Deploy\Data\ForProjects\ to E:\ProjectsData
+ expand configuration of factors from a few to full
+ no neutralization are needed
+ change test return from OPEN to CLOSE
+ using 881001.WI as market index

## factor structure

| Factor  | Input                   | data source                                | Fun                                  | Parameters               | Derived                                                                          |
|---------|-------------------------|--------------------------------------------|--------------------------------------|--------------------------|----------------------------------------------------------------------------------|
| MTM     | R                       | major_return.db                            | .                                    | None                     | Sum[T]X, Sum[T]X/Std[T]X, T=(10,20,60,120,180,240)                               |
| SIZE    | OI,contractMultiplier,P | instrument_volume.db                       | .                                    | None                     | Aver[T]X, X / Aver[T]X - 1, T=(10,20,60,120,180,240), X / X[L] - 1 L=(20,60,240) |
| OI      | OI                      | instrument_volume.db                       | .                                    | None                     | X / Aver[T]X - 1, T=(10,20,60,120,180,240), X / X[L] - 1 L=(20,60,240)           |
| BASIS   | basisRate               | fund_basis_by_instru.csv                   | .                                    | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| TS      | P,Pmin                  | major_minor.db, md_by_instru.csv           | (P/Pmin -1)*12/MonthD                | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| LIQUID  | amt,R                   | major_return.db                            | abs(R)/amt                           | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| SR      | VOL,OI                  | instrument_volume.db                       | VOL/OI                               | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| HR      | VOL,OI                  | instrument_volume.db                       | dOI/VOL                              | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| NETOI   | OI,L,S                  | instrument_volume.db, instrument_member.db | (sum(L)-sum(S))/OI                   | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| NETOIW  | OI,L,S                  | instrument_volume.db, instrument_member.db | (w_sum(L)-w_sum(S))/OI               | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| NETDOI  | OI,L,S                  | instrument_volume.db, instrument_member.db | (sum(dL)-sum(dS))/OI                 | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| NETDOIW | OI,L,S                  | instrument_volume.db, instrument_member.db | (w_sum(dL)-w_sum(dS))/OI             | None                     | Aver[T]X, X - Aver[T]X, T=(10,20,60,120,180,240), X - X[L] L=(20,60,240)         |
| SKEW    | R                       | major_return.db                            | Skew[T]R                             | T=(10,20,60,120,180,240) | X - X[L] L=(20,60,240)                                                           |
| VOL     | R                       | major_return.db                            | Std[T]R                              | T=(10,20,60,120,180,240) | X - X[L] L=(20,60,240)                                                           |
| RVOL    | open,high,low,close     | major_return.db                            | {ln(h/o)ln(h/c) + ln(l/o)ln(l/c)}[T] | T=(10,20,60,120,180,240) | X - X[L] L=(20,60,240)                                                           |
| CV      | R                       | major_return.db                            | Std[T]R/abs(Aver[T]R)                | T=(10,20,60,120,180,240) | X - X[L] L=(20,60,240)                                                           |
| CTP     | vol,oi,P                | major_return.db                            | Corr[T](vol/oi, P)                   | T=(60,120,180,240)       | X - X[L] L=(20,60,240)                                                           |
| CVP     | vol,P                   | major_return.db                            | Corr[T](vol, P)                      | T=(60,120,180,240)       | X - X[L] L=(20,60,240)                                                           |
| CSP     | R,P                     | major_return.db                            | Corr[T](Std[20]R, P)                 | T=(60,120,180,240)       | X - X[L] L=(20,60,240)                                                           |
| BETA    | R,RM                    | major_return.db, market_return             | COV[T]{R,RM}/VAR[T]{RM}              | T=(20,60,120,180,240)    | X - X[L] L=(20,60,240)                                                           |
| VAL     | P                       | major_return.db                            | AVER[20]P/Aver[T]P                   | T=(120,240,378,504)      | X - X[L] L=(20,60,240)                                                           |
| CBETA   | R,RC                    | major_return.db, forex exchange rate       | COV[T]{R,RC}/VAR[T]{RC}              | T=(120,240,378,504)      | X - X[L] L=(20,60,240)                                                           |
| IBETA   | R,RC                    | major_return.db, macro economic            | COV[T]{R,RC}/VAR[T]{RC}              | T=(120,240,378,504)      | X - X[L] L=(20,60,240)                                                           |
| MACD    | (O,H,L,C)               | major_return.db                            | MACD(F, S, ALPHA)                    | (F=10, S=20, ALPHA=0.2)  |                                                                                  |
| KDJ     | (O,H,L,C)               | major_return.db                            | KDJ(N)                               | (N=10, 15)               |                                                                                  |
| RSI     | (O,H,L,C)               | major_return.db                            | RSI(N)                               | (N=10, 15)               |                                                                                  |

## data involved

+ major: return, amt, vol, oi, P(close)
+ minor: P(close)
+ agg_by_instrument: P(close), VOL, OI, AMT
+ others: basisRate
+ instru_idx: open,high,low,close

## Class factors

+ CReaderMarketReturn
+ CReaderExchangeRate
+ CReaderMacroEconomic
+ CDbByInstrument
+ CCSVByInstrument
    + CMdByInstrument
    + CFundByInstrument

+ CFactors: Core(_set_factor_id(), _get_update_df(_get_instrument_factor_exposure())), _truncate_series(), _truncate_dataFrame()
    + CFactorsWithMajorReturn - MTM, LIQUID
        + CFactorsWithMajorReturnAndArgWin: _set_base_date()
            + SKEW: _set_factor_id(), _get_instrument_factor_exposure()
            + VOL: _set_factor_id(), _get_instrument_factor_exposure()
            + RVOL: _set_factor_id(), _get_instrument_factor_exposure()
            + CV: _set_factor_id(), _get_instrument_factor_exposure()
            + CTP: _set_factor_id(), _get_instrument_factor_exposure()
            + CVP: _set_factor_id(), _get_instrument_factor_exposure()
            + CSP: _set_factor_id(), _get_instrument_factor_exposure(), _set_base_date()
            + VAL: _set_factor_id(), _get_instrument_factor_exposure()
            + CFactorsWithMajorReturnAndMarketReturn
                + BETA: _set_factor_id(), _get_instrument_factor_exposure()
            + CFactorsWithMajorReturnAndExchangeRate
                + CBETA: _set_factor_id(), _get_instrument_factor_exposure()
            + CFactorsWithMajorReturnAndMacroEconomic
                + IBETA: _set_factor_id(), _get_instrument_factor_exposure()
    + CFactorsWithBasis - BASIS
    + CFactorsWithMajorMinorAndMdc - TS
    + CFactorsWithInstruVolume - SIZE, OI, SR, HR
    + CFactorsWithInstruVolumeAndInstruMember - NETOI, NETOIW, NETDOI, NETDOIW

+ CFactors: Core(_set_factor_id(), _get_update_df(_get_instrument_factor_exposure())), _truncate_series(), _truncate_dataFrame()
    + CFactorsTransformer:  _get_update_df(_set_base_date(), _transform())
    + CFactorsTransformerSum: _set_factor_id(), _transform()
    + CFactorsTransformerAver: _set_factor_id(), _transform()
    + CFactorsTransformerSharpe: _set_factor_id(), _transform()
    + CFactorsTransformerBreakRatio: _set_factor_id(), _transform()
    + CFactorsTransformerBreakDiff: _set_factor_id(), _transform()
    + CFactorsTransformerLagRatio: _set_factor_id(), _transform(), _set_base_date()
    + CFactorsTransformerLagDiff: _set_factor_id(), _transform(), _set_base_date()