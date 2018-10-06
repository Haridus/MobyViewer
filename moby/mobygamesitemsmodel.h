#ifndef MOBYGAMESITEMSMODEL_H
#define MOBYGAMESITEMSMODEL_H

#include <QtSql/QSqlQueryModel>

class MobyGamesItemsModelPrivate;

class MobyGamesItemsModel : public QSqlQueryModel
{
    Q_OBJECT
    Q_DECLARE_PRIVATE(MobyGamesItemsModel)

public:
    enum MobyGameDataRoles{
        StartRole = Qt::UserRole,
        IdRole,
        TitleRole,
        UrlRole,
        YearRole,
        PlatformRole,
        GenreRole,
        GameplayRole,
        NarrativeRole,
        ImagesRole,
        EndRole
    };

    MobyGamesItemsModel(QObject* parent = nullptr);
    ~MobyGamesItemsModel();

    virtual QVariant data(const QModelIndex &item, int role = Qt::DisplayRole) const;
    virtual QHash<int, QByteArray> roleNames()const;

    Q_INVOKABLE void setSource(const QString& sourcePath);
    Q_INVOKABLE void setConditions(const QString& conditions);
    Q_INVOKABLE QString conditions() const;
    Q_INVOKABLE int getTotalCount();
    Q_INVOKABLE void loadEntryes(int lowerBond, int upperBond );
    Q_INVOKABLE bool isOnline()const;

    Q_INVOKABLE void check(int index);
    Q_INVOKABLE void uncheck(int index);
    Q_INVOKABLE bool isCheched(int index);
    Q_INVOKABLE void clearcheck();

    Q_INVOKABLE void saveToFile(const QString& filePath, const QString& template_file_path = QString());

private:
    QStringList getColumnsNames()const;

private:
    MobyGamesItemsModelPrivate* d_ptr;
};

#endif // MOBYGAMESITEMSMODEL_H
