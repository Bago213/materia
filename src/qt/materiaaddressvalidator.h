// Copyright (c) 2011-2014 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef MATERIA_QT_MATERIAADDRESSVALIDATOR_H
#define MATERIA_QT_MATERIAADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class MateriaAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit MateriaAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

/** Materia address widget validator, checks for a valid materia address.
 */
class MateriaAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit MateriaAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

#endif // MATERIA_QT_MATERIAADDRESSVALIDATOR_H
