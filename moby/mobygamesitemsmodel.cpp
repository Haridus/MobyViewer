#include "mobygamesitemsmodel.h"
#include <QSqlDatabase>
#include <QDebug>
#include <functional>
#include <QSqlQuery>
#include <QFile>
#include <QFileInfo>
#include <QTextStream>
#include <QTextCodec>

class MobyGamesItemsModelPrivate
{
public:
    MobyGamesItemsModelPrivate()
    {}

    ~MobyGamesItemsModelPrivate()
    {}

public:
    QHash<int, QByteArray> roleNames;
    QHash<int, QByteArray> columnNames;
    QHash<int, int> role2column;
    QList<int>      column2role;
    QSqlDatabase db;
    QString conditions;
    QSet<int> checked;
};

//-----------------------------------------------
MobyGamesItemsModel::MobyGamesItemsModel(QObject* parent)
                    :QSqlQueryModel(parent)
                    ,d_ptr(new MobyGamesItemsModelPrivate())
{
/*  StartRole = Qt::UserRole,
    TitleRole,
    UrlRole,
    YearRole,
    PlatformRole,
    GenreRole,
    EndRole
*/
    //names that we use in qml
    d_ptr->roleNames[IdRole]    = "eid"; //not id i.e. id reserved in qml
    d_ptr->roleNames[TitleRole] = "title";
    d_ptr->roleNames[UrlRole]   = "url";
    d_ptr->roleNames[YearRole]  = "year";
    d_ptr->roleNames[PlatformRole] = "platforms";
    d_ptr->roleNames[GenreRole]    = "genre";
    d_ptr->roleNames[GameplayRole] = "gameplay";
    d_ptr->roleNames[NarrativeRole] = "narrative";
    d_ptr->roleNames[ImagesRole]    = "images";

    //names that we use in sql
    d_ptr->columnNames[IdRole]    = "id";
    d_ptr->columnNames[TitleRole] = "title";
    d_ptr->columnNames[UrlRole]   = "url";
    d_ptr->columnNames[YearRole]  = "year";
    d_ptr->columnNames[PlatformRole] = "platforms";
    d_ptr->columnNames[GenreRole]    = "genre";
    d_ptr->columnNames[GameplayRole] = "gameplay";
    d_ptr->columnNames[NarrativeRole] = "narrative";
    d_ptr->columnNames[ImagesRole]    = "images";

    //fields that we are going to show
    d_ptr->column2role.push_back(IdRole);
    d_ptr->column2role.push_back(TitleRole);
    d_ptr->column2role.push_back(UrlRole);
    d_ptr->column2role.push_back(YearRole);
    d_ptr->column2role.push_back(PlatformRole);
    d_ptr->column2role.push_back(GenreRole);
    d_ptr->column2role.push_back(GameplayRole);
    d_ptr->column2role.push_back(NarrativeRole);
    d_ptr->column2role.push_back(ImagesRole);

    //reflection for simplier coding
    d_ptr->role2column[IdRole]    = d_ptr->column2role.indexOf(IdRole);
    d_ptr->role2column[TitleRole] = d_ptr->column2role.indexOf(TitleRole);
    d_ptr->role2column[UrlRole]   = d_ptr->column2role.indexOf(UrlRole);
    d_ptr->role2column[YearRole]  = d_ptr->column2role.indexOf(YearRole);
    d_ptr->role2column[PlatformRole]  = d_ptr->column2role.indexOf(PlatformRole);
    d_ptr->role2column[GenreRole]     = d_ptr->column2role.indexOf(GenreRole);
    d_ptr->role2column[GameplayRole]  = d_ptr->column2role.indexOf(GameplayRole);
    d_ptr->role2column[NarrativeRole] = d_ptr->column2role.indexOf(NarrativeRole);
    d_ptr->role2column[ImagesRole]    = d_ptr->column2role.indexOf(ImagesRole);
}

MobyGamesItemsModel::~MobyGamesItemsModel()
{
    delete d_ptr;
}

QStringList MobyGamesItemsModel::getColumnsNames()const
{
    QStringList result;
    for(auto role : d_ptr->column2role ){
        if(d_ptr->columnNames.contains(role) ){
            result << d_ptr->columnNames[role];
        }
    }
    return result;
}

QVariant MobyGamesItemsModel::data(const QModelIndex &item, int role) const
{
    QVariant value;
    if( role > StartRole && role < EndRole ){
        int row = item.row();
        QModelIndex value_index = item.model()->index(row,d_ptr->role2column[role]);
        value = value_index.data(Qt::DisplayRole);
    }
    else{
        value = QSqlQueryModel::data(item , role);
    }
    return value;
}

QHash<int, QByteArray> MobyGamesItemsModel::roleNames()const
{
    return d_ptr->roleNames;
}

void MobyGamesItemsModel::setSource(const QString& sourcePath)
{
    if( d_ptr->db.isValid() && d_ptr->db.isOpen() ){
        d_ptr->db.close();
    }
    QSqlDatabase db = QSqlDatabase::addDatabase("QSQLITE","MobyConnection");
    db.setDatabaseName(sourcePath);
    qDebug()<<"opening database: "<<db.open();
    d_ptr->db = db;
}

void MobyGamesItemsModel::setConditions(const QString& conditions)
{
    d_ptr->conditions = conditions;
}

QString MobyGamesItemsModel::conditions() const
{
    return d_ptr->conditions;
}

int MobyGamesItemsModel::getTotalCount()
{
    int result = 0;
    if( isOnline() ){
        QString conditions = this->conditions();
        QString query;
        if( conditions.isEmpty() ){
            query = QString("SELECT MAX(id) as count FROM moby_games ");
        }
        else{
            query = QString("SELECT COUNT(id) as count FROM moby_games WHERE %1 ").arg(conditions);
        }
        qDebug()<<query;
        QSqlQuery queryObj(d_ptr->db);
        if( queryObj.exec(query) ){
            if( queryObj.next() ){
                result = queryObj.value(0).toLongLong();
            }
        }
    }
    qDebug()<<result;
    return result;
}

void MobyGamesItemsModel::loadEntryes(int lowerBond, int upperBond )
{
    if( isOnline() ){
        int count = upperBond - lowerBond+1;
        int page  = count == 0 ? 0 : lowerBond/count;
        int offset = count*page;
        QString columnsList = getColumnsNames().join(",");

        //WHERE %4 starts arg list befause if condition will contain %num construction
        //it will cause bad error due to uncorrect replacement
        QString query = d_ptr->conditions.isEmpty() ? QString("SELECT %1 FROM moby_games ORDER BY id ASC LIMIT %2 OFFSET %3").arg(columnsList).arg(count).arg(offset)
                                                    : QString("SELECT %1 FROM moby_games WHERE (%4) ORDER BY id ASC LIMIT %2 OFFSET %3").arg(columnsList).arg(count).arg(offset).arg(d_ptr->conditions);
        qDebug()<<query;
        setQuery(query,d_ptr->db);
    }
}

bool MobyGamesItemsModel::isOnline()const
{
    return d_ptr->db.isOpen();
}

void MobyGamesItemsModel::check(int index)
{
    d_ptr->checked.insert(index);
}

void MobyGamesItemsModel::uncheck(int index)
{
    d_ptr->checked.remove(index);
}

bool MobyGamesItemsModel::isCheched(int index)
{
    return d_ptr->checked.contains(index);
}

void MobyGamesItemsModel::clearcheck()
{
    d_ptr->checked.clear();
}

void MobyGamesItemsModel::saveToFile(const QString& filePath, const QString& template_file_path)
{
    if( d_ptr->checked.size() > 0) {
        QString path = filePath;
        path = path.remove("file:///");
        QFile file( path );
        if( file.open(QFile::WriteOnly | QFile::Truncate) ){
            QTextStream out_stram(&file);
            out_stram.setCodec(QTextCodec::codecForName("system"));

            QString template_string;
            if( !template_file_path.isEmpty() ){
                QFile template_file(template_file_path);
                if( template_file.open(QFile::ReadOnly) ){
                    template_string = template_file.readAll();
                }
            }
            if( template_string.isEmpty() ){
                template_string = "{title}[{year},{genre}]\n " \
                                  "{gameplay},{narrative},{platform}\n"   \
                                  "{url}\n\n";
            }

            for(auto index : d_ptr->checked ){
                //id,title,url,year,platforms,genre,gameplay,narrative,images
                QString title     = data(this->index(index,d_ptr->role2column[TitleRole])).toString();
                QString url       = data(this->index(index,d_ptr->role2column[UrlRole])).toString();
                QString year      = data(this->index(index,d_ptr->role2column[YearRole])).toString();
                QString platform  = data(this->index(index,d_ptr->role2column[PlatformRole])).toString();
                QString genre     = data(this->index(index,d_ptr->role2column[GenreRole])).toString();
                QString gameplay  = data(this->index(index,d_ptr->role2column[GameplayRole])).toString();
                QString narrative = data(this->index(index,d_ptr->role2column[NarrativeRole])).toString();

                QString output_data = template_string;

                output_data.replace("{title}",title);
                output_data.replace("{year}",year);
                output_data.replace("{genre}",genre);
                output_data.replace("{gameplay}",gameplay);
                output_data.replace("{narrative}",narrative);
                output_data.replace("{platform}",platform);
                output_data.replace("{url}",url);

                out_stram<<output_data;
            }
            out_stram.flush();
            file.close();
        }
    }
}
